import torch
import torch.nn as nn
import transformers

from .patching_utils import compute_flash_attention


def neox_forward_with_flash_attn(
    self: transformers.models.gpt_neox.modeling_gpt_neox.GPTNeoXAttention,
    flash_attn: nn.Module,  # flash_attn.modules.mha.FlashSelfAttention
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
        return out, None
    else:
        return self.old_forward(query, key, value, attention_mask, head_mask)
