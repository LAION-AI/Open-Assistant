import pydantic


class ModelConfig(pydantic.BaseModel):
    model_id: str
    max_input_length: int = 512
    max_total_length: int = 1024
    quantized: bool = False

    @property
    def is_llama(self) -> bool:
        return "llama" in self.model_id.lower()

    @property
    def is_lorem(self) -> bool:
        return self.model_id == "_lorem"

    @property
    def compat_hash(self) -> str:
        return f"{self.model_id}-{self.max_total_length}-{self.max_input_length}-{'q' if self.quantized else 'f'}"


MODEL_CONFIGS = {
    "_lorem": ModelConfig(
        model_id="_lorem",
        max_input_length=128,
        max_total_length=256,
    ),
    "distilgpt2": ModelConfig(
        model_id="distilgpt2",
        max_input_length=512,
        max_total_length=1024,
    ),
    "OA_SFT_Pythia_12B": ModelConfig(
        model_id="OpenAssistant/oasst-sft-1-pythia-12b",
        max_input_length=1024,
        max_total_length=2048,
    ),
    "OA_SFT_Pythia_12Bq": ModelConfig(
        model_id="OpenAssistant/oasst-sft-1-pythia-12b",
        max_input_length=1024,
        max_total_length=2048,
        quantized=True,
    ),
    "OA_SFT_Pythia_12B_4": ModelConfig(
        model_id="OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5",
        max_input_length=1024,
        max_total_length=2048,
    ),
    "OA_SFT_Pythia_12Bq_4": ModelConfig(
        model_id="OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5",
        max_input_length=1024,
        max_total_length=2048,
        quantized=True,
    ),
    "OA_SFT_Llama_7B": ModelConfig(
        model_id="OpenAssistant/oasst_sft_llama_7b_mask_1000",
        max_input_length=1024,
        max_total_length=2048,
    ),
    "OA_SFT_Llama_13B": ModelConfig(
        model_id="OpenAssistant/oasst_sft_llama_13b_mask_1500",
        max_input_length=1024,
        max_total_length=2048,
    ),
    "OA_SFT_Llama_13Bq": ModelConfig(
        model_id="OpenAssistant/oasst_sft_llama_13b_mask_1500",
        max_input_length=1024,
        max_total_length=2048,
        quantized=True,
    ),
    "OA_SFT_Llama_30B": ModelConfig(
        model_id="OpenAssistant/llama_30b_oasst_latcyr_1000",
        max_input_length=1024,
        max_total_length=1792,  # seeing OOMs on 2048 on an A100 80GB
    ),
    "OA_SFT_Llama_30Bq": ModelConfig(
        model_id="OpenAssistant/llama_30b_oasst_latcyr_1000",
        max_input_length=1024,
        max_total_length=1792,  # an a100 40GB can't handle 2048
        quantized=True,
    ),
    "OA_SFT_Llama_30B_2": ModelConfig(
        model_id="OpenAssistant/llama_30b_oasst_latcyr_400",
        max_input_length=1024,
        max_total_length=1792,
    ),
    "OA_SFT_Llama_30Bq_2": ModelConfig(
        model_id="OpenAssistant/llama_30b_oasst_latcyr_400",
        max_input_length=1024,
        max_total_length=1792,  # an a100 40GB can't handle 2048
        quantized=True,
    ),
    "OA_SFT_Llama_30B_5": ModelConfig(
        model_id="OpenAssistant/oasst-sft-5-llama-30b-epoch-1",
        max_input_length=1024,
        max_total_length=1792,  # seeing OOMs on 2048 on an A100 80GB
    ),
    "OA_SFT_Llama_30Bq_5": ModelConfig(
        model_id="OpenAssistant/oasst-sft-5-llama-30b-epoch-1",
        max_input_length=1024,
        max_total_length=1792,  # seeing OOMs on 2048 on an A100 80GB
        quantized=True,
    ),
    "OA_SFT_Llama_30B_6": ModelConfig(
        model_id="OpenAssistant/oasst-sft-6-llama-30b",
        max_input_length=1024,
        max_total_length=1792,  # seeing OOMs on 2048 on an A100 80GB
    ),
    "OA_SFT_Llama_30Bq_6": ModelConfig(
        model_id="OpenAssistant/oasst-sft-6-llama-30b",
        max_input_length=1024,
        max_total_length=1792,  # seeing OOMs on 2048 on an A100 80GB
        quantized=True,
    ),
    "OA_SFT_Llama_30B_7": ModelConfig(
        model_id="OpenAssistant/oasst-sft-7-llama-30b",
        max_input_length=1024,
        max_total_length=1792,  # seeing OOMs on 2048 on an A100 80GB
    ),
    "OA_SFT_Llama_30Bq_7": ModelConfig(
        model_id="OpenAssistant/oasst-sft-7-llama-30b",
        max_input_length=1024,
        max_total_length=1792,  # seeing OOMs on 2048 on an A100 80GB
        quantized=True,
    ),
    "OA_SFT_Llama_30B_7e3": ModelConfig(
        model_id="OpenAssistant/oasst-sft-7e3-llama-30b",
        max_input_length=1024,
        max_total_length=1792,  # seeing OOMs on 2048 on an A100 80GB
    ),
    "OA_RLHF_Llama_30B_2_7k": ModelConfig(
        model_id="OpenAssistant/oasst-rlhf-2-llama-30b-7k-steps",
        max_input_length=1024,
        max_total_length=1792,  # seeing OOMs on 2048 on an A100 80GB
    ),
    "Carper_RLHF_13B_1": ModelConfig(
        model_id="CarperAI/vicuna-13b-fine-tuned-rlhf",
        max_input_length=1024,
        max_total_length=2048,
    ),
    "Carper_RLHF_13Bq_1": ModelConfig(
        model_id="CarperAI/vicuna-13b-fine-tuned-rlhf",
        max_input_length=1024,
        max_total_length=2048,
        quantized=True,
    ),
    "OA_SFT_Llama2_70B_10": ModelConfig(
        model_id="OpenAssistant/llama2-70b-oasst-sft-v10",
        max_input_length=3072,
        max_total_length=4096,
    ),
    "OA_SFT_CodeLlama_13B_10": ModelConfig(
        model_id="OpenAssistant/codellama-13b-oasst-sft-v10",
        max_input_length=8192,
        max_total_length=12288,
    ),
}
