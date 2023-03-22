import fastapi
import pydantic
from oasst_shared.schemas import inference

router = fastapi.APIRouter(
    prefix="/configs",
    tags=["configs"],
)


class ParameterConfig(pydantic.BaseModel):
    name: str
    description: str = ""
    work_parameters: inference.WorkParametersInput


class ModelInfo(pydantic.BaseModel):
    name: str
    description: str = ""
    parameter_configs: list[ParameterConfig] = []


DEFAULT_PARAMETER_CONFIGS = [
    ParameterConfig(
        name="k50",
        description="Top-k sampling with k=50",
        work_parameters=inference.WorkParametersInput(
            model_name="_model_",
            top_k=50,
            top_p=0.95,
            temperature=1.0,
            repetition_penalty=1.2,
        ),
    ),
    ParameterConfig(
        name="nucleus9",
        description="Nucleus sampling with p=0.9",
        work_parameters=inference.WorkParametersInput(
            model_name="_model_",
            top_p=0.9,
            temperature=0.8,
            repetition_penalty=1.2,
        ),
    ),
    ParameterConfig(
        name="typical2",
        description="Typical sampling with p=0.2",
        work_parameters=inference.WorkParametersInput(
            model_name="_model_",
            temperature=0.8,
            typical_p=0.2,
            repetition_penalty=1.2,
        ),
    ),
    ParameterConfig(
        name="typical3",
        description="Typical sampling with p=0.3",
        work_parameters=inference.WorkParametersInput(
            model_name="_model_",
            temperature=0.8,
            typical_p=0.3,
            repetition_penalty=1.2,
        ),
    ),
]


@router.get("/models")
async def get_models() -> list[ModelInfo]:
    return [
        ModelInfo(
            name=model_name,
            parameter_configs=[
                config.copy(update={"work_parameters": config.work_parameters.copy(update={"model_name": model_name})})
                for config in DEFAULT_PARAMETER_CONFIGS
            ],
        )
        for model_name in inference.DEFAULT_MODEL_LENGTHS.keys()
    ]
