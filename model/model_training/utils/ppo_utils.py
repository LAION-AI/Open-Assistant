import inspect
from typing import List, Tuple
import transformers
import torch
from custom_datasets.formatting import QA_SPECIAL_TOKENS
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, DataCollatorWithPadding, PreTrainedTokenizer
from trlx.pipeline import BasePipeline, register_datapipeline
from trlx.trainer import register_trainer
from trlx.trainer.accelerate_ppo_trainer import AcceleratePPOTrainer
from trlx.trainer.nn.ppo_models import CausalLMHydraWithValueHead
from trlx.utils.modeling import hf_get_causal_base_model, hf_get_hidden_size, hf_get_lm_head, make_head
from utils.utils import get_model


class CustomCausalLMHydraWithValueHead(CausalLMHydraWithValueHead, torch.nn.Module):
    """The CausalLMHydraWithValueHead class implements a causal language model
    with a secondary, scalar head.
    """

    def __init__(self, config, tokenizer):
        torch.nn.Module.__init__(self)
        self.config = transformers.AutoConfig.from_pretrained(config.model_name)
        self.base_model = get_model(config, tokenizer)

        self.base_model.transformer = hf_get_causal_base_model(self.base_model)
        self.base_model.lm_head = hf_get_lm_head(self.base_model)
        dtype = next(self.base_model.lm_head.parameters()).dtype
        self.v_head = make_head(hf_get_hidden_size(self.config), 1, dtype)

        # Cache `transformer.forward` args for general use (avoids incompatible args across architectures)
        self.base_model_transformer_args = inspect.getfullargspec(self.base_model.transformer.forward).args


@register_trainer
class CustomPPOTrainer(AcceleratePPOTrainer):
    def __init__(self, config, *args, **kwargs):
        # hm...
        self.tokenizer = AutoTokenizer.from_pretrained(
            config.tokenizer.tokenizer_path, padding_side=config.tokenizer.padding_side
        )
        super().__init__(*args, config=config, **kwargs)
        self.tokenizer = AutoTokenizer.from_pretrained(
            config.tokenizer.tokenizer_path, padding_side=config.tokenizer.padding_side
        )

    def decode(
        self,
        prompts: List[torch.LongTensor],
        samples: List[torch.LongTensor],
        prompt_sizes: torch.LongTensor = None,
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Decode tensor generations into lists of strings (`samples`: List[str], `prompts`: List[str], `outputs`: List[str])
        """
        if prompt_sizes is None:
            # Assuming prompts were left-padded
            prompt_sizes = [prompts.shape[1]] * len(prompts)

        str_samples, str_prompts, str_outputs = [], [], []

        for prompt, sample, prompt_size in zip(prompts, samples, prompt_sizes):
            if self.config.model.model_arch_type == "seq2seq":
                raise NotImplementedError("Decoding for seq2seq models is not implemented yet")
                output_start_ix = 0
            else:
                output_start_ix = prompt_size

            # Skip the padding token but not the other special tokens
            PAD_TOKEN_ID = self.tokenizer.pad_token_id

            str_prompt = self.tokenizer.decode(
                prompt[:prompt_size][prompt[:prompt_size] != PAD_TOKEN_ID], skip_special_tokens=False
            )
            str_output = self.tokenizer.decode(
                sample[output_start_ix:][sample[output_start_ix:] != PAD_TOKEN_ID], skip_special_tokens=False
            )

            # Trim outputs up to `self.stop_sequences` if any are present
            if self.stop_sequences:
                for stop in self.stop_sequences:
                    stop_ix = str_output.find(stop)
                    if stop_ix >= 0:
                        str_output = str_output[:stop_ix].rstrip()

            str_prompts.append(str_prompt)
            str_outputs.append(str_output)

            if self.config.model.model_arch_type == "seq2seq":
                sample = str_prompt + self.tokenizer.sep_token + str_output
            else:
                sample = str_prompt + str_output + self.tokenizer.eos_token

            str_samples.append(sample)

        return str_samples, str_prompts, str_outputs

    def get_arch(self, config):
        # model = get_model(config.sft_config, self.tokenizer)

        if config.model.model_arch_type == "seq2seq":
            raise NotImplementedError("Seq2Seq models are not implemented yet")
            # model = Seq2SeqLMHydraWithValueHead(config.model.model_path, config.model.num_layers_unfrozen)
        else:
            model = CustomCausalLMHydraWithValueHead(config.sft_config, self.tokenizer)
            # model = CausalLMHydraWithValueHead(config.model.model_path, config.model.num_layers_unfrozen)

        model.half()

        return model

    def generate(self, input_ids, *args, **kwargs):
        preds = super().generate(input_ids, *args, **kwargs)

        # make sure the last token is the EOS token
        preds[:, -1] = self.tokenizer.eos_token_id

        return preds

    def generate_eval(self, input_ids, *args, **kwargs):
        preds = super().generate(input_ids, *args, **kwargs)

        preds[:, -1] = self.tokenizer.eos_token_id

        return preds


@register_datapipeline
class CustomPromptPipeline(BasePipeline):
    """
    Tokenizes prompts, unless they are already tokenized, and truncates them to `max_prompt_length` from the right
    """

    def __init__(self, prompts: List[str], max_prompt_length: int, tokenizer: PreTrainedTokenizer):
        super().__init__()

        model_inputs = tokenizer(
            prompts,
            truncation=True,
            padding=False,
            max_length=max_prompt_length,
            add_special_tokens=False,
        )

        prompts_tokens_ = model_inputs["input_ids"]
        attention_mask = model_inputs["attention_mask"]

        prompts_tokens = []

        assistant_token_id = tokenizer.convert_tokens_to_ids(QA_SPECIAL_TOKENS["Answer"])
        eos_token_id = tokenizer.eos_token_id

        # Due to truncation, special tokens may not be present ... so we add them (context is still incomplete)
        # not need to update attention_mask since it iw always 1
        for prompt_tokens in prompts_tokens_:
            prompts_tokens.append(prompt_tokens[:-2] + [eos_token_id, assistant_token_id])

        self.tokenizer = tokenizer
        self.prompts = [
            {"input_ids": tokens, "attention_mask": mask} for tokens, mask in zip(prompts_tokens, attention_mask)
        ]

    def __getitem__(self, ix: int):
        return self.prompts[ix]

    def __len__(self) -> int:
        return len(self.prompts)

    def create_loader(self, batch_size: int, shuffle=False) -> DataLoader:
        collate_fn = DataCollatorWithPadding(self.tokenizer) if self.tokenizer else torch.vstack
        return DataLoader(self, batch_size=batch_size, collate_fn=collate_fn, shuffle=shuffle)
