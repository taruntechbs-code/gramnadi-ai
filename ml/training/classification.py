from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier

from .metrics import classification_metrics


@dataclass
class ClassificationResult:
    model: object
    label_encoder: LabelEncoder
    metrics: dict[str, float]
    predictions: np.ndarray
    probabilities: np.ndarray


def train_classifier(
    X_train, y_train, X_validation, y_validation, params, seed, early_stopping_rounds
):
    encoder = LabelEncoder()
    encoded_train = encoder.fit_transform(y_train)
    encoded_validation = encoder.transform(y_validation)
    model_params = {
        "objective": "multi:softprob",
        "eval_metric": "mlogloss",
        "num_class": len(encoder.classes_),
        "tree_method": "hist",
        "random_state": seed,
        "n_jobs": 4,
        **params,
    }
    if early_stopping_rounds:
        model_params["early_stopping_rounds"] = early_stopping_rounds
    model = XGBClassifier(**model_params)
    model.fit(
        X_train,
        encoded_train,
        eval_set=[(X_validation, encoded_validation)],
        verbose=False,
    )
    probabilities = model.predict_proba(X_validation)
    predictions = np.argmax(probabilities, axis=1)
    metrics = classification_metrics(
        encoded_validation, predictions, probabilities, np.arange(len(encoder.classes_))
    )
    return ClassificationResult(model, encoder, metrics, predictions, probabilities)


def save_classification_plots(
    actual, predicted, probabilities, labels, output_dir: Path
) -> None:
    from sklearn.metrics import (
        ConfusionMatrixDisplay,
        PrecisionRecallDisplay,
        RocCurveDisplay,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    ConfusionMatrixDisplay.from_predictions(
        actual, predicted, display_labels=labels, xticks_rotation=45
    )
    plt.tight_layout()
    plt.savefig(output_dir / "confusion_matrix.png", dpi=140)
    plt.close()
    fig, ax = plt.subplots(figsize=(8, 6))
    for index, label in enumerate(labels):
        RocCurveDisplay.from_predictions(
            (actual == index).astype(int),
            probabilities[:, index],
            name=str(label),
            ax=ax,
        )
    fig.tight_layout()
    fig.savefig(output_dir / "roc_curve.png", dpi=140)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 6))
    for index, label in enumerate(labels):
        PrecisionRecallDisplay.from_predictions(
            (actual == index).astype(int),
            probabilities[:, index],
            name=str(label),
            ax=ax,
        )
    fig.tight_layout()
    fig.savefig(output_dir / "pr_curve.png", dpi=140)
    plt.close(fig)
