import torch


# rotary pos emb helpers (torch.jit.script does not seem to support staticmethod...)
def rotate_half(x):
    x1, x2 = x[..., : x.shape[-1] // 2], x[..., x.shape[-1] // 2 :]
    return torch.cat((-x2, x1), dim=x1.ndim - 1)  # dim=-1 triggers a bug in torch < 1.8.0


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


class LlamaLinearScaledRope(torch.nn.Module):
    """
    reference: https://huggingface.co/kaiokendev/superhot-13b-8k-no-rlhf-test
    """

    def __init__(self, dim, max_position_embeddings=2048, base=10000, scale=1, device=None):
        super().__init__()
        self.scale = 1 / scale
        inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2).float().to(device) / dim))
        self.register_buffer("inv_freq", inv_freq)

        # Build here to make `torch.jit.trace` work.
        self.max_seq_len_cached = max_position_embeddings
        t = torch.arange(self.max_seq_len_cached, device=self.inv_freq.device, dtype=self.inv_freq.dtype)
        t *= self.scale
        freqs = torch.einsum("i,j->ij", t, self.inv_freq)
        # Different from paper, but it uses a different permutation in order to obtain the same calculation
        emb = torch.cat((freqs, freqs), dim=-1)
        dtype = torch.get_default_dtype()
        self.register_buffer("cos_cached", emb.cos()[None, None, :, :].to(dtype), persistent=False)
        self.register_buffer("sin_cached", emb.sin()[None, None, :, :].to(dtype), persistent=False)

    def forward(self, x, seq_len=None):
        # x: [bs, num_attention_heads, seq_len, head_size]
        # This `if` block is unlikely to be run after we build sin/cos in `__init__`. Keep the logic here just in case.
        if seq_len > self.max_seq_len_cached:
            self.max_seq_len_cached = seq_len
            t = torch.arange(self.max_seq_len_cached, device=x.device, dtype=self.inv_freq.dtype)
            t *= self.scale
            freqs = torch.einsum("i,j->ij", t, self.inv_freq)
            # Different from paper, but it uses a different permutation in order to obtain the same calculation
            emb = torch.cat((freqs, freqs), dim=-1).to(x.device)
            self.register_buffer("cos_cached", emb.cos()[None, None, :, :].to(x.dtype), persistent=False)
            self.register_buffer("sin_cached", emb.sin()[None, None, :, :].to(x.dtype), persistent=False)
        return (
            self.cos_cached[:, :, :seq_len, ...].to(dtype=x.dtype),
            self.sin_cached[:, :, :seq_len, ...].to(dtype=x.dtype),
        )


class LlamaNTKScaledRope(torch.nn.Module):

    """
    reference: https://github.com/jquesnelle/scaled-rope
    """

    def __init__(self, dim, max_position_embeddings=2048, base=10000, alpha=1, device=None):
        super().__init__()
        base = base * alpha ** (dim / (dim - 2))
        inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2).float().to(device) / dim))
        self.register_buffer("inv_freq", inv_freq)

        # Build here to make `torch.jit.trace` work.
        self.max_seq_len_cached = max_position_embeddings
        t = torch.arange(self.max_seq_len_cached, device=self.inv_freq.device, dtype=self.inv_freq.dtype)
        freqs = torch.einsum("i,j->ij", t, self.inv_freq)
        # Different from paper, but it uses a different permutation in order to obtain the same calculation
        emb = torch.cat((freqs, freqs), dim=-1)
        dtype = torch.get_default_dtype()
        self.register_buffer("cos_cached", emb.cos()[None, None, :, :].to(dtype), persistent=False)
        self.register_buffer("sin_cached", emb.sin()[None, None, :, :].to(dtype), persistent=False)

    def forward(self, x, seq_len=None):
        # x: [bs, num_attention_heads, seq_len, head_size]
        # This `if` block is unlikely to be run after we build sin/cos in `__init__`. Keep the logic here just in case.
        if seq_len > self.max_seq_len_cached:
            self.max_seq_len_cached = seq_len
            t = torch.arange(self.max_seq_len_cached, device=x.device, dtype=self.inv_freq.dtype)
            freqs = torch.einsum("i,j->ij", t, self.inv_freq)
            # Different from paper, but it uses a different permutation in order to obtain the same calculation
            emb = torch.cat((freqs, freqs), dim=-1).to(x.device)
            self.register_buffer("cos_cached", emb.cos()[None, None, :, :].to(x.dtype), persistent=False)
            self.register_buffer("sin_cached", emb.sin()[None, None, :, :].to(x.dtype), persistent=False)
        return (
            self.cos_cached[:, :, :seq_len, ...].to(dtype=x.dtype),
            self.sin_cached[:, :, :seq_len, ...].to(dtype=x.dtype),
        )


class LlamaDynamicScaledRotaryEmbedding(torch.nn.Module):
    """
    reference: https://github.com/jquesnelle/scaled-rope
    """

    def __init__(self, dim, max_position_embeddings=2048, base=10000, ntk=False, device=None):
        super().__init__()
        self.ntk = ntk
        self.base = base
        self.dim = dim
        self.max_position_embeddings = max_position_embeddings
        inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2).float().to(device) / dim))
        self.register_buffer("inv_freq", inv_freq)

        # Build here to make `torch.jit.trace` work.
        self.max_seq_len_cached = max_position_embeddings
        t = torch.arange(self.max_seq_len_cached, device=self.inv_freq.device, dtype=self.inv_freq.dtype)
        freqs = torch.einsum("i,j->ij", t, self.inv_freq)
        # Different from paper, but it uses a different permutation in order to obtain the same calculation
        emb = torch.cat((freqs, freqs), dim=-1)
        dtype = torch.get_default_dtype()
        self.register_buffer("cos_cached", emb.cos()[None, None, :, :].to(dtype), persistent=False)
        self.register_buffer("sin_cached", emb.sin()[None, None, :, :].to(dtype), persistent=False)

    def forward(self, x, seq_len=None):
        # x: [bs, num_attention_heads, seq_len, head_size]
        # This `if` block is unlikely to be run after we build sin/cos in `__init__`. Keep the logic here just in case.
        if seq_len > self.max_seq_len_cached:
            self.max_seq_len_cached = seq_len
            if self.ntk:
                base = self.base * ((self.ntk * seq_len / self.max_position_embeddings) - (self.ntk - 1)) ** (
                    self.dim / (self.dim - 2)
                )
                inv_freq = 1.0 / (base ** (torch.arange(0, self.dim, 2).float().to(x.device) / self.dim))
                self.register_buffer("inv_freq", inv_freq)
            t = torch.arange(self.max_seq_len_cached, device=x.device, dtype=self.inv_freq.dtype)
            if not self.ntk:
                t *= self.max_position_embeddings / seq_len
            freqs = torch.einsum("i,j->ij", t, self.inv_freq)
            # Different from paper, but it uses a different permutation in order to obtain the same calculation
            emb = torch.cat((freqs, freqs), dim=-1).to(x.device)
            self.register_buffer("cos_cached", emb.cos()[None, None, :, :].to(x.dtype), persistent=False)
            self.register_buffer("sin_cached", emb.sin()[None, None, :, :].to(x.dtype), persistent=False)
        return (
            self.cos_cached[:, :, :seq_len, ...].to(dtype=x.dtype),
            self.sin_cached[:, :, :seq_len, ...].to(dtype=x.dtype),
        )
