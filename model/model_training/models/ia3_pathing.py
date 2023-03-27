from .modeling_llama import (
    LLaMAForCausalLM, 
    LLaMADecoderLayer, 
    apply_rotary_pos_emb,
)
from .configuration_llama import LLaMAConfig
from typing import Optional, Tuple
from torch import nn
import math
import torch


def _patched_mlp_forward(self, x):
    # During training we use single scale vector for the whole batch
    
    if not hasattr(self, "ff_scaler"):
        raise AttributeError("LLaMAMLP.ff_scaler is not defined")
    
    
    intermediate_inp = self.act_fn(self.gate_proj(x))
    intermediate_inp = self.ff_scaler * intermediate_inp
    
    self.down_proj(intermediate_inp * self.up_proj(x))


def _patched_self_attn_forward(self, 
                               hidden_states: torch.Tensor,
                               past_key_value: Optional[Tuple[torch.Tensor]] = None, 
                               attention_mask: Optional[torch.Tensor] = None,
                               output_attentions: bool = False,
                              ) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]:
    
    # During training we use single scale vector for the whole batch
    
    if not hasattr(self, "v_scaler"):
        raise AttributeError("LLaMADecoderLayer.v_scaler is not defined")
    
    if not hasattr(self, "k_scaler"):
        raise AttributeError("LLaMADecoderLayer.k_scaler is not defined")
    
    
    bsz, q_len, _ = hidden_states.size()

    query_states = self.q_proj(hidden_states).view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)
    key_states = self.k_proj(hidden_states).view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)
    value_states = self.v_proj(hidden_states).view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)
    # [bsz, nh, t, hd]
    
    kv_seq_len = key_states.shape[-2]
    offset = 0
    if past_key_value is not None:
        offset = past_key_value[0].shape[-2]
        kv_seq_len += offset
    cos, sin = self.rotary_emb(value_states, seq_len=kv_seq_len)
    query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin, offset=offset)
    # [bsz, nh, t, hd]

    if past_key_value is not None:
        # reuse k, v, self_attention
        key_states = torch.cat([past_key_value[0], key_states], dim=2)
        value_states = torch.cat([past_key_value[1], value_states], dim=2)

    past_key_value = (key_states, value_states)
    
    ############# PATCHED HERE #############
    
    key_states = self.k_scaler * key_states
    attn_weights = torch.matmul(query_states, key_states.transpose(2, 3)) / math.sqrt(self.head_dim)

    ########################################
    
    if attn_weights.size() != (bsz, self.num_heads, q_len, kv_seq_len):
        raise ValueError(
            f"Attention weights should be of size {(bsz * self.num_heads, q_len, kv_seq_len)}, but is"
            f" {attn_weights.size()}"
        )

    if attention_mask is not None:
        if attention_mask.size() != (bsz, 1, q_len, kv_seq_len):
            raise ValueError(
                f"Attention mask should be of size {(bsz, 1, q_len, kv_seq_len)}, but is {attention_mask.size()}"
            )
        attn_weights = attn_weights + attention_mask
        attn_weights = torch.max(attn_weights, torch.tensor(torch.finfo(attn_weights.dtype).min))

    # upcast attention to fp32
    attn_weights = nn.functional.softmax(attn_weights, dim=-1, dtype=torch.float32).to(query_states.dtype)
    
    ############# PATCHED HERE #############
    
    value_states = self.v_scaler * value_states    
    attn_output = torch.matmul(attn_weights, value_states)
    
    ############# PATCHED HERE #############
    
    if attn_output.size() != (bsz, self.num_heads, q_len, self.head_dim):
        raise ValueError(
            f"`attn_output` should be of size {(bsz, self.num_heads, q_len, self.head_dim)}, but is"
            f" {attn_output.size()}"
        )

    attn_output = attn_output.transpose(1, 2)
    attn_output = attn_output.reshape(bsz, q_len, self.hidden_size)

    attn_output = self.o_proj(attn_output)

    if not output_attentions:
        attn_weights = None

    return attn_output, attn_weights, past_key_value


def patch_model(llama_model: LLaMAForCausalLM, device=None):
    config = llama_model.config

    for param in llama_model.parameters():
        param.requires_grad = False
    
    for layer in llama_model.model.layers:
        self_attn = layer.self_attn
        mlp = layer.mlp

        head_dim = config.hidden_size // config.num_attention_heads
        self_attn.v_scaler = torch.nn.Parameter(torch.ones(head_dim, device=device))
        self_attn.k_scaler = torch.nn.Parameter(torch.ones(head_dim, device=device))

        mlp.ff_scaler = torch.nn.Parameter(torch.ones(config.intermediate_size, device=device))

        self_attn.forward = _patched_self_attn_forward
        mlp.forward = _patched_mlp_forward


def save_scalers(llama_model: LLaMAForCausalLM, filename: str):
    scalers = []
    
    for layer in llama_model.model.layers:
        self_attn = layer.self_attn
        mlp = layer.mlp
        
        scalers.append({
            "k": self_attn.k_scaler,
            "v": self_attn.v_scaler,
            "ff": mlp.ff_scaler,
        })
        
    torch.save(scalers, filename)
