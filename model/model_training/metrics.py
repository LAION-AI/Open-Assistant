import numpy as np
from scipy import stats as st


def reward_accuracy(eval_pred):
    logits = eval_pred.predictions
    labels = eval_pred.label_ids

    pos_scores,neg_scores = [],[]
    for i in np.unique(labels):
        logits_batch = logits[labels==i]
        pos_scores.append(logits_batch[0])
        neg_scores.append(logits_batch[-1])
    pos_scores = np.array(pos_scores).reshape(-1,1)
    neg_scores = np.array(neg_scores).reshape(-1,1)

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
    for i in np.unique(labels):
        logits_batch = logits[labels==i]
        pred_rank = np.argsort(logits_batch)
        true_rank = np.arange(logits_batch.size-1,-1,-1)
        tau += st.kendalltau(pred_rank, true_rank)[0]

    return {"kendalltau":tau/np.unique(labels).size}


def spearmanr(eval_pred):
    
    logits = eval_pred.predictions
    labels = eval_pred.label_ids
    score = 0.0
    for i in np.unique(labels):
        logits_batch = logits[labels==i]
        pred_rank = np.argsort(logits_batch)
        true_rank = np.arange(logits_batch.size-1,-1,-1)
        score += st.spearmanr(pred_rank, true_rank).statistic

    return {"spearmanr":score/np.unique(labels).size}


class RewardMetrics:
    
    def __init__(self,metrics):
        
        if isinstance(metrics,str):
            metrics = [metrics]

        self.metrics = []
        for name in metrics:
            if name == "accuracy":
                self.metrics.append(reward_accuracy)
            elif name == "kendalltau":
                self.metrics.append(kendall_tau)
            elif name == "spearmanr":
                self.metrics.append(spearmanr)
                
    def __call__(self,eval_pred):
        results = {}
        for metrics in self.metrics:
            results.update(metrics(eval_pred))
        
        return results