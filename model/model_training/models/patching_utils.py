import torch
import torch.nn.functional as F


def compute_flash_attention(flash_attn, q, k, v, attention_mask=None, head_mask=None):
    # q, k, v: [bs, seq_len, num_attention_heads, attn_head_size]
    # attention_mask (float): [bs, seq_len]
    batch_size, max_len = q.size(0), q.size(1)

    qkv = torch.stack([q, k, v], dim=2).to(torch.float16)  # need to truncate in case input is fp32
    cu_seqlens, max_seqlen = None, None

    if attention_mask is None:
        return flash_attn(qkv, cu_seqlens=cu_seqlens, max_seqlen=max_seqlen)
    else:
        # Limitation: non-contiguous attention mask will not be handled correctly
        # model will be able to pay attention between the first and last non-masked token, i.e. left- and right-side padding is supported.
        csums = (attention_mask >= 0).cumsum(dim=1)
        ends = csums.argmax(dim=1) + 1
        starts = ends - csums.max(dim=1).values
        seqlens = ends - starts

        qkv = torch.cat([qkv[i, starts[i] : ends[i]] for i in range(batch_size)], dim=0)
        zero = torch.zeros_like(seqlens[:1])  # torch.tensor([0]) with correct dtype and device
        cu_seqlens = torch.cat([zero, seqlens.cumsum(dim=0)], dim=0).to(torch.int32)
        max_seqlen = seqlens.max().item()

        out = flash_attn(qkv, cu_seqlens=cu_seqlens, max_seqlen=max_seqlen)
        # out: [num_unmasked_tokens, num_attention_heads, attn_head_size]

        seqs = [out[start:end] for start, end in zip(cu_seqlens[:-1], cu_seqlens[1:])]
        # stack and pad sequences together
        padded_seqs = [
            F.pad(seqs[i], (0, 0) * (seqs[i].dim() - 1) + (starts[i], max_len - ends[i]), value=0.0)
            for i in range(batch_size)
        ]
        out = torch.stack(padded_seqs)
        return out


if __name__ == "__main__":
    from flash_attn.modules.mha import FlashSelfAttention

    flash_attn = FlashSelfAttention(causal=True)

    dtype = torch.float16
    device = torch.device("cuda:0")

    batch_size, seq_len, num_heads, head_size = 4, 18, 8, 32
    q = torch.randn(batch_size, seq_len, num_heads, head_size, dtype=dtype, device=device)
    k = torch.randn(batch_size, seq_len, num_heads, head_size, dtype=dtype, device=device)
    v = torch.randn(batch_size, seq_len, num_heads, head_size, dtype=dtype, device=device)

    attn_mask = torch.randn(batch_size, seq_len, dtype=dtype, device=device).abs().cumsum(dim=1)
    attn_mask = ((attn_mask > 3) & (attn_mask < 10)).int().log()

    out = compute_flash_attention(flash_attn, q, k, v, attention_mask=attn_mask)
