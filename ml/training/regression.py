from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from xgboost import XGBRegressor

from .metrics import regression_metrics


@dataclass
class RegressionResult:
    model: XGBRegressor
    metrics: dict[str, float]
    predictions: np.ndarray


def train_regressor(
    X_train, y_train, X_validation, y_validation, params, seed, early_stopping_rounds
):
    model_params = {
        "objective": "reg:squarederror",
        "eval_metric": "rmse",
        "tree_method": "hist",
        "random_state": seed,
        "n_jobs": 4,
        **params,
    }
    if early_stopping_rounds:
        model_params["early_stopping_rounds"] = early_stopping_rounds
    model = XGBRegressor(**model_params)
    model.fit(X_train, y_train, eval_set=[(X_validation, y_validation)], verbose=False)
    predictions = model.predict(X_validation)
    return RegressionResult(
        model, regression_metrics(y_validation, predictions), predictions
    )


def save_regression_plots(actual, predicted, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    residuals = np.asarray(actual) - np.asarray(predicted)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(actual, predicted, s=8, alpha=0.35)
    bounds = [
        min(np.min(actual), np.min(predicted)),
        max(np.max(actual), np.max(predicted)),
    ]
    ax.plot(bounds, bounds, "r--")
    ax.set(
        xlabel="Actual future cash flow",
        ylabel="Predicted future cash flow",
        title="Prediction vs actual",
    )
    fig.tight_layout()
    fig.savefig(output_dir / "prediction_vs_actual.png", dpi=140)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(predicted, residuals, s=8, alpha=0.35)
    ax.axhline(0, color="red", linestyle="--")
    ax.set(
        xlabel="Predicted future cash flow", ylabel="Residual", title="Residual plot"
    )
    fig.tight_layout()
    fig.savefig(output_dir / "residual_plot.png", dpi=140)
    plt.close(fig)
