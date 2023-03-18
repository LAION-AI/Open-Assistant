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


@router.get("/models")
async def get_models() -> list[ModelInfo]:
    return [
        ModelInfo(
            name="distilgpt2",
            description="DistilGPT2 model from HuggingFace",
            parameter_configs=[
                ParameterConfig(
                    name="k50",
                    description="k=50",
                    work_parameters=inference.WorkParametersInput(
                        model_name="distilgpt2",
                        k=50,
                    ),
                ),
                ParameterConfig(
                    name="k100",
                    description="k=100",
                    work_parameters=inference.WorkParametersInput(
                        model_name="distilgpt2",
                        k=100,
                    ),
                ),
            ],
        )
    ]
