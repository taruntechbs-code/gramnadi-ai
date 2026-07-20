from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from ml.data_generator.config import GeneratorConfig


def export_dataset(frame: pd.DataFrame, config: GeneratorConfig) -> dict[str, Path]:
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    exported: dict[str, Path] = {}
    base_name = "synthetic_rural_financial_data"
    for format_name in config.export_formats:
        path = output_dir / f"{base_name}.{format_name}"
        if format_name == "csv":
            frame.to_csv(path, index=False)
        elif format_name == "parquet":
            frame.to_parquet(path, index=False)
        elif format_name == "json":
            frame.to_json(path, orient="records", date_format="iso")
        exported[format_name] = path
    return exported


def generate_analysis_report(frame: pd.DataFrame, config: GeneratorConfig) -> Path:
    """Save compact exploratory plots and machine-readable dataset statistics."""

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    report_dir = Path(config.output_dir) / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    sample = frame
    if len(frame) > config.report_sample_size:
        sample = frame.sample(config.report_sample_size, random_state=config.seed)
    sns.set_theme(style="whitegrid")

    _save_feature_distributions(sample, report_dir, plt, sns)
    _save_sector_counts(sample, report_dir, plt, sns)
    _save_risk_distribution(sample, report_dir, plt, sns)
    _save_cash_flow_distribution(sample, report_dir, plt, sns)
    _save_correlation_matrix(sample, report_dir, plt, sns)

    summary: dict[str, Any] = {
        "rows": int(len(frame)),
        "enterprises": int(frame["enterprise_id"].nunique()),
        "date_min": str(frame["month_date"].min()),
        "date_max": str(frame["month_date"].max()),
        "sector_counts": {
            str(key): int(value)
            for key, value in frame["sector"].value_counts().items()
        },
        "risk_level_counts": {
            str(key): int(value)
            for key, value in frame["risk_level"].value_counts().items()
        },
        "missing_values": {
            str(key): int(value) for key, value in frame.isna().sum().items() if value
        },
        "seed": config.seed,
    }
    summary_path = report_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return report_dir


def _save_feature_distributions(
    sample: pd.DataFrame, report_dir: Path, plt: Any, sns: Any
) -> None:
    columns = ["income", "expense", "profit", "net_cash_flow", "risk_score"]
    figure, axes = plt.subplots(2, 3, figsize=(15, 8))
    for axis, column in zip(axes.flat, columns):
        sns.histplot(sample[column], kde=True, ax=axis, color="#2f6f62")
        axis.set_title(column.replace("_", " ").title())
    axes.flat[-1].axis("off")
    figure.tight_layout()
    figure.savefig(report_dir / "feature_distributions.png", dpi=140)
    plt.close(figure)


def _save_sector_counts(
    sample: pd.DataFrame, report_dir: Path, plt: Any, sns: Any
) -> None:
    figure, axis = plt.subplots(figsize=(12, 5))
    order = sample["sector"].value_counts().index
    sns.countplot(data=sample, y="sector", order=order, ax=axis, color="#4c956c")
    axis.set_title("Enterprise-month records by sector")
    figure.tight_layout()
    figure.savefig(report_dir / "sector_counts.png", dpi=140)
    plt.close(figure)


def _save_risk_distribution(
    sample: pd.DataFrame, report_dir: Path, plt: Any, sns: Any
) -> None:
    figure, axis = plt.subplots(figsize=(8, 5))
    sns.countplot(
        data=sample,
        x="risk_level",
        order=["low", "medium", "high"],
        ax=axis,
        color="#f4a261",
    )
    axis.set_title("Ground-truth risk distribution")
    figure.tight_layout()
    figure.savefig(report_dir / "risk_distribution.png", dpi=140)
    plt.close(figure)


def _save_cash_flow_distribution(
    sample: pd.DataFrame, report_dir: Path, plt: Any, sns: Any
) -> None:
    figure, axis = plt.subplots(figsize=(9, 5))
    sns.histplot(
        data=sample,
        x="net_cash_flow",
        hue="sector",
        element="step",
        stat="density",
        common_norm=False,
        ax=axis,
    )
    axis.set_title("Monthly net cash-flow distribution")
    figure.tight_layout()
    figure.savefig(report_dir / "cash_flow_distribution.png", dpi=140)
    plt.close(figure)


def _save_correlation_matrix(
    sample: pd.DataFrame, report_dir: Path, plt: Any, sns: Any
) -> None:
    columns = [
        "income",
        "expense",
        "profit",
        "cash_balance",
        "inventory_value",
        "outstanding_loan",
        "rainfall",
        "risk_score",
        "cash_flow_after_1_month",
    ]
    correlation = sample[columns].corr()
    figure, axis = plt.subplots(figsize=(11, 8))
    sns.heatmap(correlation, cmap="vlag", center=0, annot=False, ax=axis)
    axis.set_title("Selected feature correlation matrix")
    figure.tight_layout()
    figure.savefig(report_dir / "correlation_matrix.png", dpi=140)
    plt.close(figure)
