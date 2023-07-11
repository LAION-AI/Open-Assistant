
import torch
from typing import Optional


# rotary pos emb helpers (torch.jit.script does not seem to support staticmethod...)
def rotate_half(x):
    x1, x2 = x[..., : x.shape[-1] // 2], x[..., x.shape[-1] // 2 :]
    return torch.cat((-x2, x1), dim=x1.ndim - 1)  # dim=-1 triggers a bug in torch < 1.8.0

class RWNTKScaledRotary(torch.nn.Module):

    """Implementation of RotaryEmbedding from GPT-NeoX.
    This implementation is design to operate on queries and keys that are compatible with
    [batch_size, n_heads_per_partition, seq_len, head_dim] (e.g. MinGPTAttention format).
    """

    def __init__(
        self,
        head_dim: int,
        base=10000,
        alpha:int=2,
    ):
        super().__init__()
        self.alpha = alpha
        base = base * self.alpha ** (head_dim / (head_dim-2))
        inv_freq = 1.0 / (base ** (torch.arange(0, head_dim, 2).float() / head_dim))
        self.register_buffer("inv_freq", inv_freq, persistent=False)
        self.head_dim = head_dim
        self.seq_len_cached = None
        self.batch_size_cached = None
        self.cos_cached: torch.Tensor | None = None
        self.sin_cached: torch.Tensor | None = None

    def cos_sin(
        self,
        seq_len: int,
        device="cuda",
        dtype=torch.bfloat16,
    ) -> torch.Tensor:
        if seq_len != self.seq_len_cached:
            self.seq_len_cached = seq_len
            t = torch.arange(seq_len, device=device).type_as(self.inv_freq)
            freqs = torch.einsum("i,j->ij", t, self.inv_freq)
            emb = torch.cat((freqs, freqs), dim=-1).to(device)

            if dtype in [torch.float16, torch.bfloat16]:
                emb = emb.float()

            self.cos_cached = emb.cos()[None, :, :]
            self.sin_cached = emb.sin()[None, :, :]

            self.cos_cached = self.cos_cached.type(dtype)
            self.sin_cached = self.sin_cached.type(dtype)

        return self.cos_cached, self.sin_cached

    def forward(self, q, k):
        batch, seq_len, head_dim = q.shape
        cos, sin = self.cos_sin(seq_len, q.device, q.dtype)
        return (q * cos) + (rotate_half(q) * sin), (k * cos) + (rotate_half(k) * sin)
