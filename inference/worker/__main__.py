import concurrent.futures
import signal
import sys
import time
from contextlib import closing

import pydantic
import transformers
import utils
import websocket
import work
from loguru import logger
from oasst_shared import model_configs
from oasst_shared.schemas import inference
from settings import settings


def terminate_worker(signum, frame):
    logger.warning(f"Signal {signum}. Terminating worker...")
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, terminate_worker)
    logger.info(f"Inference protocol version: {inference.INFERENCE_PROTOCOL_VERSION}")

    model_config = model_configs.MODEL_CONFIGS.get(settings.model_config_name)
    logger.warning(f"Model config: {model_config}")
    if model_config is None:
        logger.error(f"Unknown model config name: {settings.model_config_name}")
        sys.exit(2)

    if model_config.is_lorem:
        tokenizer = None
    else:
        tokenizer: transformers.PreTrainedTokenizer = transformers.AutoTokenizer.from_pretrained(model_config.model_id)
        logger.warning(f"Tokenizer {tokenizer.name_or_path} vocab size: {len(tokenizer)}")

    inference_http = utils.HttpClient(
        base_url=settings.inference_server_url,
        basic_auth_username=settings.basic_auth_username,
        basic_auth_password=settings.basic_auth_password,
        bearer_token=settings.bearer_token,
    )

    while True:
        try:
            if not model_config.is_lorem:
                utils.wait_for_inference_server(inference_http)

            if settings.perform_oom_test:
                work.perform_oom_test(tokenizer)
                sys.exit(0)

            worker_config = inference.WorkerConfig(
                model_config=model_config,
                max_parallel_requests=settings.max_parallel_requests,
            )

            logger.warning(f"connecting to {settings.backend_url}...")
            with closing(
                websocket.create_connection(
                    f"{settings.backend_url}/workers/work",
                    header={
                        "X-API-Key": settings.api_key,
                        "X-Protocol-Version": inference.INFERENCE_PROTOCOL_VERSION,
                    },
                )
            ) as ws:
                logger.warning("Connected to backend, sending config...")
                worker_info = inference.WorkerInfo(
                    config=worker_config,
                    hardware_info=inference.WorkerHardwareInfo(),
                )
                utils.send_response(ws, worker_info)
                logger.warning("Config sent, waiting for work...")

                with concurrent.futures.ThreadPoolExecutor(max_workers=worker_config.max_parallel_requests) as executor:
                    ftrs = []
                    while True:
                        if ftrs:
                            done, not_done = concurrent.futures.wait(ftrs, timeout=1)
                            ftrs = list(not_done)
                            for ftr in done:
                                ftr.result()
                        message = ws.recv()
                        if not message:
                            logger.warning("Connection closed, reconnecting...")
                            break
                        worker_request = pydantic.parse_raw_as(inference.WorkerRequest, message)
                        match worker_request.request_type:
                            case "work":
                                logger.info(f"Handling work request: {worker_request.id=}")
                                ftr = executor.submit(
                                    work.handle_work_request, ws, tokenizer, worker_request, worker_config
                                )
                                ftrs.append(ftr)
                            case "ping":
                                utils.send_response(
                                    ws,
                                    inference.PongResponse(
                                        request_id=worker_request.id, metrics=inference.WorkerMetricsInfo()
                                    ),
                                )
                            case "wrong_api_key":
                                logger.error("Your API Key seems to be wrong, please check it!")
                                raise RuntimeError("Your API Key seems to be wrong, please check it!")
                            case "upgrade_protocol":
                                logger.error("Your worker is outdated, please upgrade it!")
                                sys.exit(2)  # potentially read this status code outside
                            case "terminate":
                                logger.info("Received terminate, terminating worker")
                                sys.exit(0)
                            case "error":
                                logger.error(f"Received error: {worker_request.error}")
                                raise RuntimeError(f"Received error: {worker_request.error}")

        except websocket.WebSocketBadStatusException as e:
            logger.error(f"Bad status: {e.status_code=} {str(e)=}")
            logger.error("Did you provide the correct API key?")
            if not settings.retry_on_error:
                sys.exit(1)
            time.sleep(5)
        except Exception:
            logger.exception("Error in websocket")
            if not settings.retry_on_error:
                sys.exit(1)
            logger.warning("Retrying in 5 seconds...")
            time.sleep(5)


if __name__ == "__main__":
    main()
