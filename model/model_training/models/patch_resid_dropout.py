import warnings
from functools import partial
from typing import Callable

import torch.nn as nn
from transformers import GPTNeoXForCausalLM, GPTNeoXModel

SUPPORTED_MODELS = [
    GPTNeoXModel,
    GPTNeoXForCausalLM,
]


def _patched_mlp_forward(old_forward: Callable, post_module: nn.Module, module: nn.Module, *args, **kwargs):
    post_module.train(module.training)
    out = old_forward(*args, **kwargs)
    out = post_module(out)
    return out


def _patched_attn_forward(old_forward: Callable, post_module: nn.Module, module: nn.Module, *args, **kwargs):
    post_module.train(module.training)
    out = old_forward(*args, **kwargs)
    hiddens = post_module(out[0])
    return (hiddens,) + out[1:]


def add_dropout(module: nn.Module, patched_fwd: Callable, p_dropout: float = 0.1):
    dropout = nn.Dropout(p=p_dropout)
    _forward = module.forward
    module.forward = partial(patched_fwd, _forward, dropout, module)


def patch_model(model: GPTNeoXModel, resid_pdrop: float = 0.1):
    if not any(isinstance(model, model_class) for model_class in SUPPORTED_MODELS):
        warnings.warn(
            "Patching residual dropout has only been tested with this model class. "
            f"Please make sure that it also works for `{model.__class__.__name__}`."
        )

    if isinstance(model, GPTNeoXForCausalLM):
        model = model.gpt_neox

    for layer in model.layers:
        add_dropout(layer.attention, _patched_attn_forward, resid_pdrop)
        add_dropout(layer.mlp, _patched_mlp_forward, resid_pdrop)
