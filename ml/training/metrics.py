from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    f1_score,
    matthews_corrcoef,
    mean_absolute_error,
    mean_absolute_percentage_error,
    median_absolute_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
    root_mean_squared_error,
)


def regression_metrics(actual: np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    return {
        "mae": float(mean_absolute_error(actual, predicted)),
        "rmse": float(root_mean_squared_error(actual, predicted)),
        "r2": float(r2_score(actual, predicted)),
        "mape": float(mean_absolute_percentage_error(actual, predicted)),
        "median_absolute_error": float(median_absolute_error(actual, predicted)),
    }


def classification_metrics(
    actual, predicted, probabilities, labels
) -> dict[str, float]:
    result = {
        "accuracy": float(accuracy_score(actual, predicted)),
        "precision": float(
            precision_score(actual, predicted, average="weighted", zero_division=0)
        ),
        "recall": float(
            recall_score(actual, predicted, average="weighted", zero_division=0)
        ),
        "f1": float(f1_score(actual, predicted, average="weighted", zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(actual, predicted)),
        "matthews_correlation_coefficient": float(matthews_corrcoef(actual, predicted)),
    }
    try:
        result["roc_auc"] = float(
            roc_auc_score(actual, probabilities, multi_class="ovr", labels=labels)
        )
        result["pr_auc"] = float(
            average_precision_score(actual, probabilities, average="weighted")
        )
    except ValueError:
        result["roc_auc"] = float("nan")
        result["pr_auc"] = float("nan")
    return result
