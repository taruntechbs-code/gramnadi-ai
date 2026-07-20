from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from ml.feature_engineering.utils import write_json


def profile_dataset(
    frame: pd.DataFrame,
    reports_dir: Path,
    target_columns: tuple[str, ...],
    generate_plots: bool = True,
) -> dict[str, Any]:
    reports_dir.mkdir(parents=True, exist_ok=True)
    numeric = frame.select_dtypes(include="number")
    feature_summary = _column_summary(frame)
    correlation = numeric.corr()
    correlation.to_csv(reports_dir / "correlation_matrix.csv")

    profile: dict[str, Any] = {
        "rows": int(frame.shape[0]),
        "columns": int(frame.shape[1]),
        "memory_usage_bytes": int(frame.memory_usage(deep=True).sum()),
        "dtypes": {str(column): str(dtype) for column, dtype in frame.dtypes.items()},
        "column_summary": feature_summary,
        "target_correlation": _target_correlation(correlation, target_columns),
        "sector_distribution": _value_counts(frame, "sector"),
        "enterprise_distribution": _distribution_summary(frame, "enterprise_id"),
        "weather_distribution": _value_counts(frame, "weather_condition"),
        "commodity_distribution": _numeric_summary(
            frame, [column for column in frame.columns if column.endswith("_price")]
        ),
        "risk_distribution": _value_counts(frame, "risk_level"),
        "cash_flow_distribution": _numeric_summary(frame, ["net_cash_flow"]),
        "loan_distribution": _value_counts(frame, "loan_type"),
        "time_coverage": _time_coverage(frame),
    }
    write_json(reports_dir / "dataset_profile.json", profile)
    pd.DataFrame.from_dict(feature_summary, orient="index").to_csv(
        reports_dir / "feature_summary.csv", index_label="feature"
    )
    if generate_plots:
        _generate_plots(frame, reports_dir)
    return profile


def _column_summary(frame: pd.DataFrame) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    numeric = frame.select_dtypes(include="number")
    for column in frame.columns:
        series = frame[column]
        item: dict[str, Any] = {
            "dtype": str(series.dtype),
            "missing_count": int(series.isna().sum()),
            "missing_pct": round(float(series.isna().mean() * 100), 4),
            "unique_values": int(series.nunique(dropna=True)),
        }
        if column in numeric:
            values = numeric[column]
            item.update(
                {
                    "min": float(values.min()),
                    "max": float(values.max()),
                    "mean": float(values.mean()),
                    "median": float(values.median()),
                    "std": float(values.std(ddof=0)),
                    "percentiles": {
                        "p01": float(values.quantile(0.01)),
                        "p25": float(values.quantile(0.25)),
                        "p50": float(values.quantile(0.50)),
                        "p75": float(values.quantile(0.75)),
                        "p99": float(values.quantile(0.99)),
                    },
                }
            )
        summary[str(column)] = item
    return summary


def _target_correlation(
    correlation: pd.DataFrame, targets: tuple[str, ...]
) -> dict[str, dict[str, float]]:
    available = [column for column in targets if column in correlation.columns]
    if not available:
        return {}
    return correlation[available].round(6).to_dict()


def _value_counts(frame: pd.DataFrame, column: str) -> dict[str, int]:
    if column not in frame:
        return {}
    return {
        str(key): int(value)
        for key, value in frame[column].value_counts(dropna=False).items()
    }


def _distribution_summary(frame: pd.DataFrame, column: str) -> dict[str, float | int]:
    if column not in frame:
        return {}
    counts = frame[column].value_counts()
    return {
        "unique": int(counts.size),
        "rows_per_entity_min": int(counts.min()),
        "rows_per_entity_max": int(counts.max()),
        "rows_per_entity_mean": float(counts.mean()),
        "rows_per_entity_median": float(counts.median()),
    }


def _numeric_summary(
    frame: pd.DataFrame, columns: list[str]
) -> dict[str, dict[str, float]]:
    available = [column for column in columns if column in frame]
    if not available:
        return {}
    return frame[available].describe().round(4).to_dict()


def _time_coverage(frame: pd.DataFrame) -> dict[str, Any]:
    if "month_date" not in frame:
        return {}
    dates = pd.to_datetime(frame["month_date"])
    return {
        "min": str(dates.min()),
        "max": str(dates.max()),
        "unique_months": int(dates.dt.to_period("M").nunique()),
    }


def _generate_plots(frame: pd.DataFrame, reports_dir: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    sns.set_theme(style="whitegrid")
    distribution_dir = reports_dir / "feature_distributions"
    distribution_dir.mkdir(parents=True, exist_ok=True)
    for column in ["income", "expense", "profit", "net_cash_flow", "risk_score"]:
        if column not in frame:
            continue
        figure, axis = plt.subplots(figsize=(8, 5))
        sns.histplot(frame[column].dropna(), kde=True, ax=axis, color="#2f6f62")
        axis.set_title(f"Distribution: {column}")
        figure.tight_layout()
        figure.savefig(distribution_dir / f"{column}.png", dpi=130)
        plt.close(figure)

    numeric = frame.select_dtypes(include="number")
    figure, axis = plt.subplots(figsize=(13, 10))
    sns.heatmap(numeric.corr(), cmap="vlag", center=0, ax=axis)
    axis.set_title("Numeric feature correlation heatmap")
    figure.tight_layout()
    figure.savefig(reports_dir / "correlation_heatmap.png", dpi=130)
    plt.close(figure)
