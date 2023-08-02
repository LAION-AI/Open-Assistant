from __future__ import annotations  # To make it not choke over FlashSelfAttention

import warnings
from functools import partial
from typing import Callable, Optional

import torch.nn as nn
import transformers
from transformers import (
    AutoConfig,
    FalconForCausalLM,
    FalconModel,
    GPTNeoXForCausalLM,
    GPTNeoXModel,
    LlamaForCausalLM,
    LlamaModel,
)
from transformers.models.llama.modeling_llama import (
    LlamaDynamicNTKScalingRotaryEmbedding,
    LlamaLinearScalingRotaryEmbedding,
)
from trlx.models.modeling_ppo import AutoModelForCausalLMWithHydraValueHead

from .patching_falcon import falcon_forward_with_flash_attn
from .patching_llama import llama_forward_with_flash_attn
from .patching_neox import neox_forward_with_flash_attn
from .reward_model import GPTNeoXRewardModel
from .rope import RWNTKScaledRope

SUPPORTED_MODELS = [
    GPTNeoXModel,
    GPTNeoXForCausalLM,
    LlamaForCausalLM,
    LlamaModel,
    FalconForCausalLM,
    FalconModel,
    GPTNeoXRewardModel,
    # Currently only supported by NeoX models; Will work on LLaMa models
    AutoModelForCausalLMWithHydraValueHead,
]


def _patched_mlp_forward(post_module: nn.Module, module: nn.Module, *args, **kwargs):
    post_module.train(module.training)
    out = module.old_forward(*args, **kwargs)
    out = post_module(out)
    return out


def _patched_attn_forward(post_module: nn.Module, module: nn.Module, *args, **kwargs):
    post_module.train(module.training)
    out = module.old_forward(*args, **kwargs)
    hiddens = post_module(out[0])
    return (hiddens,) + out[1:]


def add_dropout(module: nn.Module, patched_fwd: Callable, p_dropout: float = 0.1):
    dropout = nn.Dropout(p=p_dropout)
    module.old_forward = module.forward
    module.forward = partial(patched_fwd, dropout, module)


def add_flash_attn(module: nn.Module, causal: bool = True):
    """
    Replaces the standard attention implementation with Flash Attention [1].
    Limitations:
      - Only works for fp16 or bf16 inputs
      - Requires inputs to be on CUDA
      - `output_attentions=True` does not work after patching, attention weights will be None
      - Non-contiguous attention masks are not supported (e.g. [1, 1, 0, 1, 1, 0, 0] will just become [1, 1, 1, 1, 1, 0, 0]).

    [1] https://github.com/HazyResearch/flash-attention
    """

    flash_attn = FlashSelfAttention(causal=causal)
    if isinstance(module, transformers.models.llama.modeling_llama.LlamaAttention):
        module.old_forward = module.forward
        module.forward = partial(llama_forward_with_flash_attn, module, flash_attn)
    elif isinstance(module, transformers.models.gpt_neox.modeling_gpt_neox.GPTNeoXAttention):
        if not hasattr(module, "_attn"):
            warnings.warn("Provided module doesn't have a _attn() function to be patched.")
        module._attn = partial(neox_forward_with_flash_attn, module, flash_attn)
    elif isinstance(module, transformers.models.falcon.modeling_falcon.FalconAttention):
        module.forward = partial(falcon_forward_with_flash_attn, module, flash_attn)
    else:
        raise NotImplementedError(f"Flash attention is not implemented for {module.__class__.__name__}.")


def patch_model(
    model: nn.Module,
    resid_pdrop: Optional[float] = 0.1,
    flash_attention: bool = True,
    patch_unsupported: bool = False,
    residual_dropout_lima: bool = False,
):
    """
    Helper function for patching HF language models.
    Currently supports: GPTNeoX-based models

    Limitations:
      - Flash attention requires CUDA and fp16/bf16 training. It also requires contiguous attention masks.
      - Residual dropout does not support multi-GPU training without DeepDpeed.
    """
    global FlashSelfAttention
    if flash_attention:
        try:
            from flash_attn.modules.mha import FlashSelfAttention  # pyright: reportMissingImports=false
        except ModuleNotFoundError:
            warnings.warn(
                """\nmodule flash_attn not found - either install:
  pip3 install flash_attn
or run with:
  --use_flash_attention=false """
            )
            exit(1)
    if (resid_pdrop is None or resid_pdrop == 0.0) and not flash_attention:
        print("Continuing without patching")
        return

    if resid_pdrop is not None and (resid_pdrop < 0 or resid_pdrop > 1.0):
        raise ValueError("Invalid argument: `resid_pdrop` must be between 0.0 and 1.0")

    if not flash_attention and (resid_pdrop is None or resid_pdrop == 0.0):
        return

    if (
        not any(isinstance(model, model_class) for model_class in SUPPORTED_MODELS)
        and model.__class__.__name__ != "RWForCausalLM"
    ):
        if not flash_attention and (resid_pdrop is None or resid_pdrop == 0.0):
            return  # nothing to patch

        if not patch_unsupported:
            warnings.warn(
                "Model patching does not support this model class. No patches will be applied. "
                "If you want to force patch this model, please set `patch_unsupported=True`."
            )
            return

        warnings.warn(
            "Patching residual dropout has only been tested with this model class. "
            f"Please make sure that it also works for `{model.__class__.__name__}`.\n"
            "Or disable flash_attention and residual_dropout with:\n"
            "--use_flash_attention=false  --no-residual_dropout"
        )

    if isinstance(model, GPTNeoXRewardModel) or isinstance(model, GPTNeoXForCausalLM):
        model = model.gpt_neox

    if isinstance(model, LlamaForCausalLM):
        model = model.model

    if isinstance(model, AutoModelForCausalLMWithHydraValueHead):
        if isinstance(model.base_model, GPTNeoXForCausalLM):
            model = model.base_model.gpt_neox
        elif isinstance(model.base_model, LlamaForCausalLM):
            model = model.base_model.model
        else:
            warnings.warn(
                "Unfortunately there is currently only support for NeoX models and LLaMa models "
                f"Please make sure that `{model.__class__.__name__}` is one of those model.\n"
                "Or disable flash_attention and residual_dropout with:\n"
                "--use_flash_attention=false  --no-residual_dropout"
            )

    if model.__class__.__name__ == "RWForCausalLM":
        model = model.base_model

    if isinstance(model, FalconForCausalLM):
        model = model.transformer

    attention_key_lookup = {
        GPTNeoXModel: "attention",
        GPTNeoXRewardModel: "attention",
        LlamaModel: "self_attn",
        FalconModel: "self_attention",
    }
    mlp_key_lookup = {
        GPTNeoXModel: "mlp",
        GPTNeoXRewardModel: "mlp",
        LlamaModel: "mlp",
        FalconModel: "mlp",
    }
    if isinstance(model, FalconModel) or model.__class__.__name__ == "RWModel":
        layers = model.h
        attention_key = "self_attention"
        mlp_key = "mlp"
    else:
        layers = model.layers
        attention_key = attention_key_lookup.get(model.__class__, "attention")
        mlp_key = mlp_key_lookup.get(model.__class__, "mlp")
    num_layers = len(layers)
    resid_pdrop_last_layer = resid_pdrop
    for i, layer in enumerate(layers):
        if flash_attention:
            add_flash_attn(getattr(layer, attention_key), causal=True)
        if residual_dropout_lima:
            resid_pdrop = i / (num_layers - 1) * resid_pdrop_last_layer
        if resid_pdrop is not None and resid_pdrop > 0:
            add_dropout(getattr(layer, attention_key), _patched_attn_forward, resid_pdrop)
            add_dropout(getattr(layer, mlp_key), _patched_mlp_forward, resid_pdrop)


class RopePatch:
    def __init__(self, model_name, **kwargs):
        self.args = kwargs
        self.rope_type = self.args.pop("type")
        config = AutoConfig.from_pretrained(model_name, trust_remote_code=True)
        if hasattr(config, "max_position_embeddings"):
            self.args["max_position_embeddings"] = config.max_position_embeddings
        if hasattr(config, "base"):
            self.args["base"] = config.base
        architecture = config.architectures
        if architecture:
            self.model_name = architecture[0]
            if "FalconForCausalLM" in architecture or "RWForCausalLM" in architecture:
                self.architecture = "FalconForCausalLM"
                if self.rope_type == "ntk":
                    self.patch_fun = RWNTKScaledRope
                else:
                    raise NotImplementedError()
            elif "LlamaForCausalLM" in architecture:
                self.architecture = "LlamaForCausalLM"
                if self.rope_type == "linear":
                    self.patch_fun = LlamaLinearScalingRotaryEmbedding
                elif self.rope_type == "dynamic":
                    self.patch_fun = LlamaDynamicNTKScalingRotaryEmbedding
                else:
                    raise NotImplementedError()
            else:
                raise NotImplementedError()

    @classmethod
    def from_config(cls, config):
        model_name = config.model_name
        args = config.superhot_config
        return cls(model_name, **args)

    def patch(self, model):
        if self.architecture == "FalconForCausalLM":
            self.patch_falcon_model(model, **self.args)
        elif self.architecture == "LlamaForCausalLM":
            self.patch_llama_model(model, **self.args)
        else:
            raise NotImplementedError()

    def patch_falcon_model(self, model, **kwargs):
        for each in model.transformer.h:
            each.self_attention.maybe_rotary = self.patch_fun(model.config.head_dim, **kwargs)

    def patch_llama_model(self, model, **kwargs):
        kwargs.update({"device": model.device})
        for each in model.model.layers:
            each.self_attn.rotary_emb = self.patch_fun(each.self_attn.head_dim, **kwargs)
