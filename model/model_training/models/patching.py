from __future__ import annotations  # To make it not choke over FlashSelfAttention

import warnings
from functools import partial
from typing import Callable, Optional

import torch
import torch.nn as nn
import transformers
from transformers import GPTNeoXForCausalLM, GPTNeoXModel, LlamaForCausalLM, LlamaModel
from trlx.models.modeling_ppo import AutoModelForCausalLMWithHydraValueHead
import trlx

from .patching_llama import llama_forward_with_flash_attn, llama_forward_with_flash_attn_rl
from .patching_utils import compute_flash_attention
from .reward_model import GPTNeoXRewardModel

SUPPORTED_MODELS = [
    GPTNeoXModel,
    GPTNeoXForCausalLM,
    LlamaForCausalLM,
    LlamaModel,
    GPTNeoXRewardModel,
    #Currently only supported by NeoX models; Will work on LLaMa models
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


def _patched_gpt_neox_attn(
    self: transformers.models.gpt_neox.modeling_gpt_neox.GPTNeoXAttention,
    flash_attn: FlashSelfAttention,
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    attention_mask=None,
    head_mask=None,
):
    # query, key, value: [bs, num_attention_heads, seq_len, attn_head_size]
    flash_attn.train(self.training)
    out_dtype = value.dtype
    q, k, v = query.transpose(1, 2), key.transpose(1, 2), value.transpose(1, 2)
    if attention_mask is not None:
        attention_mask = attention_mask[:, 0, 0, :]
    out = compute_flash_attention(flash_attn, q, k, v, attention_mask)
    out = out.transpose(1, 2).to(out_dtype)
    return out, None


def _patched_gpt_neox_attn_rl(
    self: transformers.models.gpt_neox.modeling_gpt_neox.GPTNeoXAttention,
    flash_attn: FlashSelfAttention,
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    attention_mask=None,
    head_mask=None,
):
    # query, key, value: [bs, num_attention_heads, seq_len, attn_head_size]
    if query.shape == key.shape:
        flash_attn.train(self.training)
        out_dtype = value.dtype
        q, k, v = query.transpose(1, 2), key.transpose(1, 2), value.transpose(1, 2)
        if attention_mask is not None:
            attention_mask = attention_mask[:, 0, 0, :]
        out = compute_flash_attention(flash_attn, q, k, v, attention_mask)
        out = out.transpose(1, 2).to(out_dtype)
    else:
        #If shapes don't match we use regular self attention; 
        batch_size, num_attention_heads, query_length, attn_head_size = query.size()
        key_length = key.size(-2)

        causal_mask = self.bias[:, :, key_length - query_length : key_length, :key_length]

        query = query.view(batch_size * num_attention_heads, query_length, attn_head_size)
        key = key.view(batch_size * num_attention_heads, key_length, attn_head_size)
        attn_scores = torch.zeros(
            batch_size * num_attention_heads,
            query_length,
            key_length,
            dtype=query.dtype,
            device=key.device,
        )
        attn_scores = torch.baddbmm(
            attn_scores,
            query,
            key.transpose(1, 2),
            beta=1.0,
            alpha=(torch.tensor(1.0, dtype=self.norm_factor.dtype, device=self.norm_factor.device) / self.norm_factor),
        )
        attn_scores = attn_scores.view(batch_size, num_attention_heads, query_length, key_length)

        mask_value = torch.finfo(attn_scores.dtype).min
        # Need to be a tensor, otherwise we get error: `RuntimeError: expected scalar type float but found double`.
        # Need to be on the same device, otherwise `RuntimeError: ..., x and y to be on the same device`
        mask_value = torch.tensor(mask_value, dtype=attn_scores.dtype).to(attn_scores.device)
        attn_scores = torch.where(causal_mask, attn_scores, mask_value)

        if attention_mask is not None:
            # Apply the attention mask
            attn_scores = attn_scores + attention_mask

        attn_weights = nn.functional.softmax(attn_scores, dim=-1)
        attn_weights = attn_weights.to(value.dtype)

        # Mask heads if we want to
        if head_mask is not None:
            attn_weights = attn_weights * head_mask

        out = torch.matmul(attn_weights, value)
    return out, None

def add_dropout(module: nn.Module, patched_fwd: Callable, p_dropout: float = 0.1):
    dropout = nn.Dropout(p=p_dropout)
    module.old_forward = module.forward
    module.forward = partial(patched_fwd, dropout, module)


def add_flash_attn(module: nn.Module, causal: bool = True, mode: str = "sft"):
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
        if mode == "rl":
            module.old_forward = module.forward
            module.forward = partial(llama_forward_with_flash_attn_rl, module, flash_attn)
        else:
            module.old_forward = module.forward
            module.forward = partial(llama_forward_with_flash_attn, module, flash_attn)
    elif isinstance(module, transformers.models.gpt_neox.modeling_gpt_neox.GPTNeoXAttention):
        if mode == "rl":
            if not hasattr(module, "_attn"):
                warnings.warn("Provided module doesn't have a _attn() function to be patched.")
            module._attn = partial(_patched_gpt_neox_attn_rl, module, flash_attn)
        else:    
            if not hasattr(module, "_attn"):
                warnings.warn("Provided module doesn't have a _attn() function to be patched.")
            module._attn = partial(_patched_gpt_neox_attn, module, flash_attn)
    else:
        raise NotImplementedError(f"Flash attention is not implemented for {module.__class__.__name__}.")


def patch_model(
    model: nn.Module, resid_pdrop: Optional[float] = 0.1, flash_attention: bool = True, patch_unsupported: bool = False, mode: str = "sft"
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
            add_flash_attn(getattr(layer, attention_key), causal=True, mode=mode)

        if resid_pdrop is not None and resid_pdrop > 0:
            add_dropout(getattr(layer, attention_key), _patched_attn_forward, resid_pdrop)
            add_dropout(getattr(layer, mlp_key), _patched_mlp_forward, resid_pdrop)
