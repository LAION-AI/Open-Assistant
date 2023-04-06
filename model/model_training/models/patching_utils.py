import torch
import torch.nn.functional as F
from torch.nn.utils.rnn import pad_sequence


def compute_flash_attention(flash_attn, q, k, v, attention_mask=None, head_mask=None):
    # q, k, v: [bs, seq_len, num_attention_heads, attn_head_size]
    # attention_mask (float): [bs, seq_len]
    batch_size, max_len = q.size(0), q.size(1)
    qkv = torch.stack([q, k, v], dim=2).to(torch.float16)  # need to truncate in case input is fp32
    cu_seqlens, max_seqlen = None, None

    if attention_mask is not None:
        # Limitation: attention mask can have "holes", which is currently not handled correctly
        # model will be able to pay attention up to the last non-masked token, even if previous tokens are masked.
        seqlens = (attention_mask >= 0).cumsum(dim=1).argmax(dim=1) + 1
        qkv = torch.cat([qkv[i, : seqlens[i]] for i in range(batch_size)], dim=0)
        cu_seqlens = torch.cat([torch.zeros_like(seqlens[:1]), seqlens.cumsum(dim=0)], dim=0).to(torch.int32)
        max_seqlen = seqlens.max().item()

    out = flash_attn(qkv, cu_seqlens=cu_seqlens, max_seqlen=max_seqlen)
    # out: [bs, seq_len, num_attention_heads, attn_head_size]

    if attention_mask is not None:
        seqs = [out[start:end] for start, end in zip(cu_seqlens[:-1], cu_seqlens[1:])]
        # stack and pad sequences together
        out = pad_sequence(seqs, batch_first=True)
        # restore original sequence length in case there was padding on all sequences initially
        out = F.pad(out, (0, 0) * (out.dim() - 2) + (0, max_len - out.size(1)), value=0.0)
    return out
