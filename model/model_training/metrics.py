import numpy as np
from scipy import stats as st

RM_METRICS = ["accuracy", "kendalltau", "spearmanr"]


def reward_accuracy(eval_pred):
    logits = eval_pred.predictions
    labels = eval_pred.label_ids
    pos_scores, neg_scores = [], []
    for b_logits, b_labels in zip(logits, labels):
        b_labels = b_labels[b_labels != -100]
        b_logits = b_logits[b_logits != -100]
        for i in np.unique(b_labels):
            logits_batch = b_logits[b_labels == i]
            pos_scores.append(logits_batch[0])
            neg_scores.append(logits_batch[-1])
    pos_scores = np.array(pos_scores).reshape(-1, 1)
    neg_scores = np.array(neg_scores).reshape(-1, 1)

    metrics = {
        "pos_score": np.mean(pos_scores),
        "neg_score": np.mean(neg_scores),
        "score_diff": np.mean(pos_scores - neg_scores),
        "accuracy": np.mean(pos_scores > neg_scores),
    }
    return metrics


def kendall_tau(eval_pred):
    logits = eval_pred.predictions
    labels = eval_pred.label_ids
    tau = 0.0
    bsize = 0
    for b_logits, b_labels in zip(logits, labels):
        b_labels = b_labels[b_labels != -100]
        b_logits = b_logits[b_logits != -100]
        for i in np.unique(b_labels):
            logits_batch = b_logits[b_labels == i]
            pred_rank = np.argsort(logits_batch)
            true_rank = np.arange(logits_batch.size - 1, -1, -1)
            tau += st.kendalltau(pred_rank, true_rank)[0]
        bsize += np.unique(b_labels).size

    return {"kendalltau": tau / bsize}


def spearmanr(eval_pred):
    logits = eval_pred.predictions
    labels = eval_pred.label_ids
    score = 0.0
    bsize = 0
    for b_logits, b_labels in zip(logits, labels):
        b_labels = b_labels[b_labels != -100]
        b_logits = b_logits[b_logits != -100]
        for i in np.unique(b_labels):
            logits_batch = b_logits[b_labels == i]
            pred_rank = np.argsort(logits_batch)
            true_rank = np.arange(logits_batch.size - 1, -1, -1)
            score += st.spearmanr(pred_rank, true_rank).statistic
        bsize += np.unique(b_labels).size

    return {"spearmanr": score / bsize}


class RewardMetrics:
    """
    class to combine multiple metrics
    """

    def __init__(self, metrics):
        if isinstance(metrics, str):
            metrics = [metrics]

        self.metrics = []
        for name in metrics:
            if name == "accuracy":
                self.metrics.append(reward_accuracy)
            elif name == "kendalltau":
                self.metrics.append(kendall_tau)
            elif name == "spearmanr":
                self.metrics.append(spearmanr)
            else:
                raise ValueError(f"Invalid metrics {name}. Available {RM_METRICS}")

    def __call__(self, eval_pred):
        results = {}
        for metric in self.metrics:
            results.update(metric(eval_pred))

        return results
