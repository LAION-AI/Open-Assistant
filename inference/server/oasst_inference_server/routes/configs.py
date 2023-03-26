import fastapi
import pydantic
from oasst_inference_server.settings import settings
from oasst_shared import model_configs
from oasst_shared.schemas import inference

router = fastapi.APIRouter(
    prefix="/configs",
    tags=["configs"],
)


class ParameterConfig(pydantic.BaseModel):
    name: str
    description: str = ""
    sampling_parameters: inference.SamplingParameters


class ModelConfigInfo(pydantic.BaseModel):
    name: str
    description: str = ""
    parameter_configs: list[ParameterConfig] = []


DEFAULT_PARAMETER_CONFIGS = [
    ParameterConfig(
        name="k50",
        description="Top-k sampling with k=50",
        sampling_parameters=inference.SamplingParameters(
            top_k=50,
            top_p=0.95,
            temperature=1.0,
            repetition_penalty=1.2,
        ),
    ),
    ParameterConfig(
        name="nucleus9",
        description="Nucleus sampling with p=0.9",
        sampling_parameters=inference.SamplingParameters(
            top_p=0.9,
            temperature=0.8,
            repetition_penalty=1.2,
        ),
    ),
    ParameterConfig(
        name="typical2",
        description="Typical sampling with p=0.2",
        sampling_parameters=inference.SamplingParameters(
            temperature=0.8,
            typical_p=0.2,
            repetition_penalty=1.2,
        ),
    ),
    ParameterConfig(
        name="typical3",
        description="Typical sampling with p=0.3",
        sampling_parameters=inference.SamplingParameters(
            temperature=0.8,
            typical_p=0.3,
            repetition_penalty=1.2,
        ),
    ),
]


@router.get("/model_configs")
async def get_model_configs() -> list[ModelConfigInfo]:
    return [
        ModelConfigInfo(
            name=model_config_name,
            parameter_configs=DEFAULT_PARAMETER_CONFIGS,
        )
        for model_config_name in model_configs.MODEL_CONFIGS
        if (settings.allowed_model_config_names == "*" or model_config_name in settings.allowed_model_config_names_list)
    ]
