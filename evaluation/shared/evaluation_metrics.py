"""
Evaluation metrics for model performance assessment.

Provides precision, recall, and F1 score calculations for token-based
evaluation of model outputs.
"""

from dataclasses import dataclass
from typing import List, Set, Tuple


@dataclass
class EvaluationResult:
    """Container for evaluation metrics."""
    precision: float
    recall: float
    f1: float


def calculate_token_metrics(ground_truth_tokens: List[str], predicted_tokens: List[str]) -> EvaluationResult:
    """
    Calculate precision, recall, and F1 score for token sets.

    Uses set intersection to compute token-level metrics. This is a common
    approach for evaluating open-ended text generation tasks.

    Args:
        ground_truth_tokens: List of ground truth tokens
        predicted_tokens: List of predicted tokens

    Returns:
        EvaluationResult with precision, recall, and F1 scores

    Examples:
        >>> gt = ['the', 'quick', 'brown', 'fox']
        >>> pred = ['quick', 'brown', 'dog']
        >>> result = calculate_token_metrics(gt, pred)
        >>> result.precision
        0.6666666666666666
        >>> result.recall
        0.5
    """
    gt_set: Set[str] = set(ground_truth_tokens)
    pred_set: Set[str] = set(predicted_tokens)

    # Find common tokens
    common: Set[str] = gt_set.intersection(pred_set)

    # Handle no overlap case
    if not common:
        return EvaluationResult(precision=0.0, recall=0.0, f1=0.0)

    # Calculate precision: what fraction of predicted tokens are correct
    precision = len(common) / len(pred_set) if pred_set else 0.0

    # Calculate recall: what fraction of ground truth tokens are predicted
    recall = len(common) / len(gt_set) if gt_set else 0.0

    # Calculate F1: harmonic mean of precision and recall
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) else 0.0

    return EvaluationResult(precision=precision, recall=recall, f1=f1)


def calculate_batch_metrics(
    ground_truth_list: List[List[str]],
    predicted_list: List[List[str]]
) -> Tuple[List[float], List[float], List[float]]:
    """
    Calculate metrics for a batch of samples.

    Args:
        ground_truth_list: List of ground truth token lists
        predicted_list: List of predicted token lists

    Returns:
        Tuple of (precision_scores, recall_scores, f1_scores)

    Raises:
        ValueError: If lists have different lengths
    """
    if len(ground_truth_list) != len(predicted_list):
        raise ValueError(
            f"Mismatched lengths: ground_truth={len(ground_truth_list)}, "
            f"predicted={len(predicted_list)}"
        )

    precision_scores: List[float] = []
    recall_scores: List[float] = []
    f1_scores: List[float] = []

    for gt_tokens, pred_tokens in zip(ground_truth_list, predicted_list):
        result = calculate_token_metrics(gt_tokens, pred_tokens)
        precision_scores.append(result.precision)
        recall_scores.append(result.recall)
        f1_scores.append(result.f1)

    return precision_scores, recall_scores, f1_scores


def calculate_macro_metrics(
    precision_scores: List[float],
    recall_scores: List[float],
    f1_scores: List[float]
) -> dict:
    """
    Calculate macro-averaged metrics.

    Macro-averaging computes the metric independently for each sample
    then takes the average (treats all samples equally).

    Args:
        precision_scores: List of per-sample precision scores
        recall_scores: List of per-sample recall scores
        f1_scores: List of per-sample F1 scores

    Returns:
        Dictionary with macro_precision, macro_recall, macro_f1

    Raises:
        ValueError: If any list is empty
    """
    if not precision_scores or not recall_scores or not f1_scores:
        raise ValueError("Score lists cannot be empty")

    return {
        "macro_precision": sum(precision_scores) / len(precision_scores),
        "macro_recall": sum(recall_scores) / len(recall_scores),
        "macro_f1": sum(f1_scores) / len(f1_scores)
    }
