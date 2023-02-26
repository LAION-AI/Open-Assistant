import datetime
import enum
import platform
import random
from typing import Literal

import psutil
import pydantic
import pynvml

INFERENCE_PROTOCOL_VERSION = "1"
DEFAULT_MODEL_NAME = "distilgpt2"


def compat_hash(*, model_name: str) -> str:
    return f"{model_name}"


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
    model_name: str = DEFAULT_MODEL_NAME
    hardware_info: WorkerHardwareInfo = pydantic.Field(default_factory=WorkerHardwareInfo)

    @property
    def compat_hash(self) -> str:
        return compat_hash(model_name=self.model_name)


class WorkParameters(pydantic.BaseModel):
    model_name: str = DEFAULT_MODEL_NAME
    max_new_tokens: int = 100
    do_sample: bool = True
    top_k: int = 50
    top_p: float = 0.9
    temperature: float = 1.0
    repetition_penalty: float | None = None
    seed: int = pydantic.Field(default_factory=lambda: random.randint(0, 0xFFFF_FFFF_FFFF_FFFF - 1))


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


class MessageRead(pydantic.BaseModel):
    id: str
    content: str | None
    role: Literal["prompter", "assistant"]
    state: MessageState
    vote: Vote | None
    report: Report | None

    @property
    def is_assistant(self) -> bool:
        return self.role == "assistant"


class Thread(pydantic.BaseModel):
    messages: list[MessageRead]


class WorkRequest(pydantic.BaseModel):
    thread: Thread = pydantic.Field(..., repr=False)
    created_at: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.utcnow)
    parameters: WorkParameters = pydantic.Field(default_factory=WorkParameters)


class TokenResponse(pydantic.BaseModel):
    text: str
    log_prob: float
    token_id: int


class GeneratedTextResponse(pydantic.BaseModel):
    text: str
    finish_reason: Literal["length", "eos_token", "stop_sequence"]


class WorkResponsePacket(pydantic.BaseModel):
    token: TokenResponse | None = None
    generated_text: GeneratedTextResponse | None = None
    is_end: bool = False
    error: str | None = None
