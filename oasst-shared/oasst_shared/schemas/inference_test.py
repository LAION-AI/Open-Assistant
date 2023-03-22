from . import inference


def test_create_worker_config():
    config = inference.WorkerConfig(
        model_name="distilgpt2",
    )
    assert config.model_max_total_length == 1024
    assert config.model_max_input_length == 512
