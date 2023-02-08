import torch
import torch.nn.functional as F
from torch import nn


class CrossEntropyLoss(nn.CrossEntropyLoss):
    def __init__(self, weight=None, size_average=None, ignore_index=-100, reduce=None, reduction="mean"):
        super().__init__(weight, size_average, ignore_index, reduce, reduction)

    def forward(self, input, target, mask=None):
        if mask is not None:
            mask = mask.view(-1).bool()
            input = input.view(-1, input.size(-1))
            target = target.view(-1)
            input = input[mask]
            target = target[mask]
        return super().forward(input, target)


class PolyLoss(nn.Module):
    def __init__(self, weight=None, size_average=None, ignore_index=-100, reduce=None, reduction="mean", epsilon=1.0):
        super().__init__()
        self.weight = torch.tensor(weight)
        self.ignore_index = ignore_index
        self.reduction = reduction
        self.cross_entropy = CrossEntropyLoss(weight, size_average, ignore_index, reduce, "none")
        self.epsilon = epsilon

    def forward(self, input, target, mask=None):
        if mask is not None:
            mask = mask.view(-1).bool()
            input = input.view(-1, input.size(-1))
            target = target.view(-1)
            input = input[mask]
            target = target[mask]

        onehot_target = F.one_hot(target, num_classes=input.size(-1)).to(device=input.device, dtype=input.dtype)
        pt = torch.sum(onehot_target * F.softmax(input, -1), -1)
        CE = self.cross_entropy(input, target)
        poly1 = CE + self.epsilon * (1 - pt)
        if self.reduction == "mean":
            poly1 = poly1.mean()
        elif self.reduction == "sum":
            poly1 = poly1.sum()
        return poly1
