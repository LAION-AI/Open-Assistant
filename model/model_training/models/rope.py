import torch


# rotary pos emb helpers (torch.jit.script does not seem to support staticmethod...)
def rotate_half(x):
    x1, x2 = x[..., : x.shape[-1] // 2], x[..., x.shape[-1] // 2 :]
    return torch.cat((-x2, x1), dim=-1)


class RWNTKScaledRope(torch.nn.Module):

    """
    NTK-Scaled RoPE for RefinedWebModel
    """

    def __init__(
        self,
        head_dim: int,
        base=10000,
        alpha: int = 2,
    ):
        super().__init__()
        self.alpha = alpha
        base = base * self.alpha ** (head_dim / (head_dim - 2))
        inv_freq = 1.0 / (base ** (torch.arange(0, head_dim, 2).float() / head_dim))
        self.register_buffer("inv_freq", inv_freq, persistent=False)
        self.head_dim = head_dim
        self.seq_len_cached = -1
        self.batch_size_cached = None
        self.cos_cached: torch.Tensor | None = None
        self.sin_cached: torch.Tensor | None = None

    def cos_sin(
        self,
        seq_len: int,
        past_key_values_length: int,
        device="cuda",
        dtype=torch.bfloat16,
    ) -> torch.Tensor:
        total_length = seq_len + past_key_values_length
        if total_length > self.seq_len_cached:
            self.seq_len_cached = total_length
            t = torch.arange(total_length, device=device, dtype=self.inv_freq.dtype)
            freqs = torch.einsum("i,j->ij", t, self.inv_freq)
            emb = torch.cat((freqs, freqs), dim=-1).to(device)

            if dtype in [torch.float16, torch.bfloat16]:
                emb = emb.float()

            self.cos_cached = emb.cos()[None, :, :]
            self.sin_cached = emb.sin()[None, :, :]

            self.cos_cached = self.cos_cached.type(dtype)
            self.sin_cached = self.sin_cached.type(dtype)

        return (
            self.cos_cached[:, past_key_values_length : seq_len + past_key_values_length],
            self.sin_cached[:, past_key_values_length : seq_len + past_key_values_length],
        )

    def forward(self, q, k, past_key_values_length=0):
        batch, seq_len, head_dim = q.shape
        cos, sin = self.cos_sin(seq_len, past_key_values_length, q.device, q.dtype)
        return (q * cos) + (rotate_half(q) * sin), (k * cos) + (rotate_half(k) * sin)
