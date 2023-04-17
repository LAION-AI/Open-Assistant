from __future__ import annotations  # To make it not choke over FlashSelfAttention

import warnings
from functools import partial
from typing import Callable, Optional

import torch.nn as nn
import transformers
from transformers import GPTNeoXForCausalLM, GPTNeoXModel, LlamaForCausalLM, LlamaModel
from trlx.models.modeling_ppo import AutoModelForCausalLMWithHydraValueHead

from .patching_llama import llama_forward_with_flash_attn
from .patching_neox import neox_forward_with_flash_attn
from .reward_model import GPTNeoXRewardModel

SUPPORTED_MODELS = [
    GPTNeoXModel,
    GPTNeoXForCausalLM,
    LlamaForCausalLM,
    LlamaModel,
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
    else:
        raise NotImplementedError(f"Flash attention is not implemented for {module.__class__.__name__}.")


def patch_model(
    model: nn.Module,
    resid_pdrop: Optional[float] = 0.1,
    flash_attention: bool = True,
    patch_unsupported: bool = False,
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

    if not any(isinstance(model, model_class) for model_class in SUPPORTED_MODELS):
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

    attention_key_lookup = {
        GPTNeoXModel: "attention",
        GPTNeoXRewardModel: "attention",
        LlamaModel: "self_attn",
    }
    mlp_key_lookup = {
        GPTNeoXModel: "mlp",
        GPTNeoXRewardModel: "mlp",
        LlamaModel: "mlp",
    }
    attention_key = attention_key_lookup.get(model.__class__, "attention")
    mlp_key = mlp_key_lookup.get(model.__class__, "mlp")

    for layer in model.layers:
        if flash_attention:
            add_flash_attn(getattr(layer, attention_key), causal=True)

        if resid_pdrop is not None and resid_pdrop > 0:
            add_dropout(getattr(layer, attention_key), _patched_attn_forward, resid_pdrop)
            add_dropout(getattr(layer, mlp_key), _patched_mlp_forward, resid_pdrop)
