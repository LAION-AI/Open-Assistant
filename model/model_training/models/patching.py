from __future__ import annotations  # To make it not choke over FlashSelfAttention

import warnings
from functools import partial
from typing import Callable, Optional

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.utils.rnn import pad_sequence
from transformers import GPTNeoXForCausalLM, GPTNeoXModel, LlamaForCausalLM, LlamaModel

from .reward_model import GPTNeoXRewardModel

SUPPORTED_MODELS = [
    GPTNeoXModel,
    GPTNeoXForCausalLM,
    LlamaForCausalLM,
    LlamaModel,
    GPTNeoXRewardModel,
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
    module: nn.Module,
    flash_attn: FlashSelfAttention,
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    attention_mask=None,
    head_mask=None,
):
    # query, key, value: [bs, num_attention_heads, seq_len, attn_head_size]
    flash_attn.train(module.training)
    out_dtype = value.dtype
    batch_size, max_len = query.size(0), query.size(2)

    q, k, v = query.transpose(1, 2), key.transpose(1, 2), value.transpose(1, 2)
    qkv = torch.stack([q, k, v], dim=2).to(torch.float16)  # need to truncate here since rotary embeddings are fp32
    cu_seqlens, max_seqlen = None, None

    if attention_mask is not None:
        # Limitation: attention mask can have "holes", which is currently not handled correctly
        # model will be able to pay attention up to the last non-masked token, even if previous tokens are masked.
        seqlens = (attention_mask[:, 0, 0, :] == 0).cumsum(dim=1).argmax(dim=1) + 1
        qkv = torch.cat([qkv[i, : seqlens[i]] for i in range(batch_size)], dim=0)
        cu_seqlens = torch.cat([torch.zeros_like(seqlens[:1]), seqlens.cumsum(dim=0)], dim=0).to(torch.int32)
        max_seqlen = seqlens.max().item()

    out = flash_attn(qkv, cu_seqlens=cu_seqlens, max_seqlen=max_seqlen)
    # out: [bs, seq_len, num_attention_heads, attn_head_size]

    if attention_mask is not None:
        seqs = [out[start:end] for start, end in zip(cu_seqlens[:-1], cu_seqlens[1:])]
        out = pad_sequence(seqs, batch_first=True)
        # restore original sequence length
        out = F.pad(out, (0, 0) * (out.dim() - 2) + (0, max_len - out.size(1)), value=0.0)
    out = out.transpose(1, 2).to(out_dtype)
    return out, None


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

    if not hasattr(module, "_attn"):
        warnings.warn("Provided module doesn't have a _attn() function to be patched.")
    flash_attn = FlashSelfAttention(causal=causal)
    module._attn = partial(_patched_gpt_neox_attn, module, flash_attn)


def patch_model(
    model: nn.Module, resid_pdrop: Optional[float] = 0.1, flash_attention: bool = True, patch_unsupported: bool = False
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
        if resid_pdrop is not None and resid_pdrop > 0:
            add_dropout(getattr(layer, attention_key), _patched_attn_forward, resid_pdrop)
            add_dropout(getattr(layer, mlp_key), _patched_mlp_forward, resid_pdrop)

        if flash_attention:
            if isinstance(model, LlamaModel):
                warnings.warn("Flash attention is not supported for LLaMA models.")
            else:
                add_flash_attn(layer.attention, causal=True)
