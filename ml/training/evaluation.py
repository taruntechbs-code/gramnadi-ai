from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import log_loss

from .metrics import classification_metrics, regression_metrics


def evaluate_regression(model, X, y):
    predictions = model.predict(X)
    return regression_metrics(y, predictions), predictions


def evaluate_classification(model, encoder, X, y):
    actual = encoder.transform(y)
    probabilities = model.predict_proba(X)
    predictions = np.argmax(probabilities, axis=1)
    metrics = classification_metrics(
        actual, predictions, probabilities, np.arange(len(encoder.classes_))
    )
    metrics["log_loss"] = float(
        log_loss(actual, probabilities, labels=np.arange(len(encoder.classes_)))
    )
    return metrics, predictions, probabilities, actual


def save_learning_curve(model, output_dir: Path) -> None:
    history = getattr(model, "evals_result_", {})
    if not history:
        return
    dataset = next(iter(history))
    metric = next(iter(history[dataset]))
    values = history[dataset][metric]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(values, label=f"validation {metric}")
    ax.set(xlabel="Boosting round", ylabel=metric, title="Learning curve")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "learning_curve.png", dpi=140)
    plt.close(fig)
