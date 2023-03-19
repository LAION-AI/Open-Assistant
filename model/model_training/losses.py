import torch
import torch.nn.functional as F
from torch import nn


class CrossEntropyLoss(nn.CrossEntropyLoss):
    def __init__(self, weight=None, size_average=None, ignore_index=-100, reduce=None, reduction="mean"):
        super().__init__(weight, size_average, ignore_index, reduce, "none")
        self._reduction = reduction

    def forward(self, input, target, mask=None):
        input = input.view(-1, input.size(-1))
        target = target.view(-1)

        if mask is not None:
            mask = mask.view(-1).bool()
            input = input[mask]
            target = target[mask]

        size = target.numel()

        loss = super().forward(input, target)

        if self._reduction == "none":
            return loss
        return loss.sum() / (size + 1e-8)


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


class RMLoss(nn.Module):
    def __init__(self, reduction="mean", beta=0.001):
        super().__init__()
        self.reduction = reduction
        self.beta = beta

    def forward(self, logits, cu_lengths=None):
        # if cu_lengths is None, assume that all examples belong to the same conversation
        if cu_lengths is None:
            cu_lengths = [0, logits.size(0)]

        device = logits.device
        losses = []
        for start, end in zip(cu_lengths[:-1], cu_lengths[1:]):
            pairs = torch.combinations(torch.arange(end - start, device=device), 2)
            pos_ids, neg_ids = pairs[:, 0], pairs[:, 1]
            pos_logits = logits.take(start + pos_ids)
            neg_logits = logits.take(start + neg_ids)

            l2 = 0.5 * (pos_logits**2 + neg_logits**2)
            _loss = (-F.logsigmoid(pos_logits - neg_logits) + self.beta * l2).mean()
            losses.append(_loss)
        loss = torch.stack(losses)

        if self.reduction == "none":
            return loss
        return loss.mean()
