import functools

import torch
from transformers.activations import FastGELUActivation, GELUActivation, NewGELUActivation, QuickGELUActivation


def rsetattr(obj, attr, val):
    pre, _, post = attr.rpartition(".")
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)


def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)

    return functools.reduce(_getattr, [obj] + attr.split("."))


def fuse_gelu(model):
    @torch.jit.script
    def gelu_fwd(x):
        return x * 0.5 * (1.0 + torch.tanh(0.79788456 * x * (1 + 0.044715 * x * x)))

    @torch.jit.script
    def gelu_bwd(g, x):
        tanh_out = torch.tanh(0.79788456 * x * (1 + 0.044715 * x * x))
        ff = 0.5 * x * ((1 - tanh_out * tanh_out) * (0.79788456 + 0.1070322243 * x * x)) + 0.5 * (1 + tanh_out)
        return ff * g

    class _FusedGeLUFunction(torch.autograd.Function):
        @staticmethod
        # bias is an optional argument
        def forward(ctx, input):
            ctx.input_tensor = input
            return gelu_fwd(input)

        @staticmethod
        def backward(ctx, grad_output):
            input = ctx.input_tensor
            tmp = gelu_bwd(grad_output, input)
            return tmp

    class FusedGelu(torch.nn.Module):
        def forward(self, input):
            return _FusedGeLUFunction.apply(input)

    fused_gelu_module = FusedGelu()
    hf_gelu_functions = [GELUActivation, FastGELUActivation, NewGELUActivation, QuickGELUActivation]

    for name, module in model.named_modules():
        for hf_gelu_function in hf_gelu_functions:
            if isinstance(module, hf_gelu_function):
                rsetattr(model, name, fused_gelu_module)

    return model
