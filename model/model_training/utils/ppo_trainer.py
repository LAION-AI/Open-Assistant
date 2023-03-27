from typing import List, Tuple

import torch
from transformers import AutoTokenizer
from trlx.trainer import register_trainer
from trlx.trainer.accelerate_ppo_trainer import AcceleratePPOTrainer
from trlx.trainer.nn.ppo_models import CausalLMHydraWithValueHead, Seq2SeqLMHydraWithValueHead


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

            str_prompt = self.tokenizer.decode(
                prompt[torch.where(prompt > 0)[0][0].item() : prompt_size], skip_special_tokens=False
            )
            str_output = self.tokenizer.decode(sample[output_start_ix:], skip_special_tokens=False)

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
            model = Seq2SeqLMHydraWithValueHead(config.model.model_path, config.model.num_layers_unfrozen)
        else:
            model = CausalLMHydraWithValueHead(config.model.model_path, config.model.num_layers_unfrozen)

        return model
