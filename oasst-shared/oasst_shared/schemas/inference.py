import enum
import platform
import random
import uuid
from datetime import datetime
from typing import Annotated, Literal, Union

import psutil
import pydantic
import pynvml
from oasst_shared.model_configs import ModelConfig

INFERENCE_PROTOCOL_VERSION = "1"


class WorkerGpuInfo(pydantic.BaseModel):
    name: str
    total_memory: int


class WorkerHardwareInfo(pydantic.BaseModel):
    uname_sysname: str
    uname_release: str
    uname_version: str
    uname_machine: str
    uname_processor: str
    cpu_count_physical: int
    cpu_count_logical: int
    cpu_freq_max: float
    cpu_freq_min: float
    mem_total: int
    swap_total: int
    nvidia_driver_version: str | None = None
    gpus: list[WorkerGpuInfo]

    def __init__(self, **data):
        data["uname_sysname"] = platform.uname().system
        data["uname_release"] = platform.uname().release
        data["uname_version"] = platform.uname().version
        data["uname_machine"] = platform.uname().machine
        data["uname_processor"] = platform.uname().processor
        data["cpu_count_physical"] = psutil.cpu_count(logical=False)
        data["cpu_count_logical"] = psutil.cpu_count(logical=True)
        data["cpu_freq_max"] = psutil.cpu_freq().max
        data["cpu_freq_min"] = psutil.cpu_freq().min
        data["mem_total"] = psutil.virtual_memory().total
        data["swap_total"] = psutil.swap_memory().total
        data["gpus"] = []
        try:
            pynvml.nvmlInit()
            data["nvidia_driver_version"] = pynvml.nvmlSystemGetDriverVersion()
            for i in range(pynvml.nvmlDeviceGetCount()):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle)
                total_memory = pynvml.nvmlDeviceGetMemoryInfo(handle).total
                data["gpus"].append(WorkerGpuInfo(name=name, total_memory=total_memory))
        except Exception:
            pass
        super().__init__(**data)


class WorkerConfig(pydantic.BaseModel):
    model_config: ModelConfig
    max_parallel_requests: int = 1

    @property
    def compat_hash(self) -> str:
        return self.model_config.compat_hash


class WorkerInfo(pydantic.BaseModel):
    config: WorkerConfig
    hardware_info: WorkerHardwareInfo


class GpuMetricsInfo(pydantic.BaseModel):
    gpu_usage: float
    mem_usage: float


class WorkerMetricsInfo(pydantic.BaseModel):
    created_at: datetime
    cpu_usage: float
    mem_usage: float
    swap_usage: float
    gpus: list[GpuMetricsInfo] | None = None

    def __init__(self, **data):
        data["created_at"] = datetime.utcnow()
        data["cpu_usage"] = psutil.cpu_percent()
        data["mem_usage"] = psutil.virtual_memory().percent
        data["swap_usage"] = psutil.swap_memory().percent
        try:
            pynvml.nvmlInit()
            data["nvidia_driver_version"] = pynvml.nvmlSystemGetDriverVersion()
            gpus = []
            for i in range(pynvml.nvmlDeviceGetCount()):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                gpus.append(
                    {
                        "gpu_usage": pynvml.nvmlDeviceGetUtilizationRates(handle).gpu,
                        "mem_usage": pynvml.nvmlDeviceGetMemoryInfo(handle).used,
                    }
                )
            data["gpus"] = gpus
        except Exception:
            pass
        super().__init__(**data)


class SamplingParameters(pydantic.BaseModel):
    top_k: int | None = None
    top_p: float | None = None
    typical_p: float | None = None
    temperature: float | None = None
    repetition_penalty: float | None = None
    max_new_tokens: int = 1024


def make_seed() -> int:
    return random.randint(0, 0xFFFF_FFFF_FFFF_FFFF - 1)


class WorkParameters(pydantic.BaseModel):
    model_config: ModelConfig
    sampling_parameters: SamplingParameters = pydantic.Field(default_factory=SamplingParameters)
    do_sample: bool = True
    seed: int = pydantic.Field(
        default_factory=make_seed,
    )


class ReportType(str, enum.Enum):
    spam = "spam"
    offensive = "offensive"
    feeback = "feedback"


class Vote(pydantic.BaseModel):
    id: str
    score: int


class Report(pydantic.BaseModel):
    id: str
    type: ReportType
    reason: str


class MessageState(str, enum.Enum):
    manual = "manual"
    pending = "pending"
    in_progress = "in_progress"
    complete = "complete"
    aborted_by_worker = "aborted_by_worker"
    cancelled = "cancelled"
    timeout = "timeout"


class MessageRead(pydantic.BaseModel):
    id: str
    parent_id: str | None
    content: str | None
    created_at: datetime
    role: Literal["prompter", "assistant"]
    state: MessageState
    score: int
    reports: list[Report] = []

    @property
    def is_assistant(self) -> bool:
        return self.role == "assistant"


class Thread(pydantic.BaseModel):
    messages: list[MessageRead]


class WorkerRequestBase(pydantic.BaseModel):
    id: str = pydantic.Field(default_factory=lambda: str(uuid.uuid4()))


class WorkRequest(WorkerRequestBase):
    request_type: Literal["work"] = "work"
    thread: Thread = pydantic.Field(..., repr=False)
    created_at: datetime = pydantic.Field(default_factory=datetime.utcnow)
    parameters: WorkParameters = pydantic.Field(default_factory=WorkParameters)


class PingRequest(WorkerRequestBase):
    request_type: Literal["ping"] = "ping"


class ErrorRequest(WorkerRequestBase):
    request_type: Literal["error"] = "error"
    error: str


class UpgradeProtocolRequest(WorkerRequestBase):
    request_type: Literal["upgrade_protocol"] = "upgrade_protocol"


class WrongApiKeyRequest(WorkerRequestBase):
    request_type: Literal["wrong_api_key"] = "wrong_api_key"


class TerminateRequest(WorkerRequestBase):
    request_type: Literal["terminate"] = "terminate"


class WorkerResponseBase(pydantic.BaseModel):
    request_id: str | None = None


class PongResponse(WorkerResponseBase):
    response_type: Literal["pong"] = "pong"
    metrics: WorkerMetricsInfo | None = None


class TokenResponse(WorkerResponseBase):
    response_type: Literal["token"] = "token"
    text: str
    log_prob: float | None
    token_id: int


class GeneratedTextResponse(WorkerResponseBase):
    response_type: Literal["generated_text"] = "generated_text"
    text: str
    finish_reason: Literal["length", "eos_token", "stop_sequence"]
    metrics: WorkerMetricsInfo | None = None


class InternalFinishedMessageResponse(WorkerResponseBase):
    response_type: Literal["internal_finished_message"] = "internal_finished_message"
    message: MessageRead


class InternalErrorResponse(WorkerResponseBase):
    response_type: Literal["internal_error"] = "internal_error"
    error: str
    message: MessageRead


class ErrorResponse(WorkerResponseBase):
    response_type: Literal["error"] = "error"
    metrics: WorkerMetricsInfo | None = None
    error: str


class GeneralErrorResponse(WorkerResponseBase):
    response_type: Literal["general_error"] = "general_error"
    metrics: WorkerMetricsInfo | None = None
    error: str


_WorkerRequest = Union[
    WorkRequest,
    PingRequest,
    ErrorRequest,
    TerminateRequest,
    UpgradeProtocolRequest,
    WrongApiKeyRequest,
]
WorkerRequest = Annotated[
    _WorkerRequest,
    pydantic.Field(discriminator="request_type"),
]

WorkerResponse = Annotated[
    Union[
        TokenResponse,
        GeneratedTextResponse,
        ErrorResponse,
        PongResponse,
        InternalFinishedMessageResponse,
        InternalErrorResponse,
    ],
    pydantic.Field(discriminator="response_type"),
]
