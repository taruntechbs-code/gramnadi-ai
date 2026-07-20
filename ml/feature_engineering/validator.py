from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from ml.feature_engineering.config import (
    EXPECTED_SECTORS,
    IDENTIFIER_COLUMNS,
    TARGET_COLUMNS,
)


class DatasetValidationError(ValueError):
    """Raised when required structural validation fails."""


@dataclass(frozen=True)
class ValidationResult:
    report: dict[str, Any]
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.errors


REQUIRED_COLUMNS = {
    "enterprise_id",
    "sector",
    "month_date",
    "income",
    "expense",
    "profit",
    "inventory_value",
    "outstanding_loan",
    "temperature",
    "rainfall",
    *TARGET_COLUMNS,
}

NON_NEGATIVE_COLUMNS = (
    "income",
    "expense",
    "savings",
    "inventory_value",
    "principal_amount",
    "monthly_installment",
    "outstanding_loan",
)

NUMERIC_COLUMNS = (
    "income",
    "expense",
    "profit",
    "savings",
    "cash_balance",
    "inventory_value",
    "upi_transaction_count",
    "upi_inflow",
    "upi_outflow",
    "risk_score",
    "cash_flow_after_1_month",
    "cash_flow_after_3_month",
    "cash_flow_after_6_month",
)


def validate_dataset(frame: pd.DataFrame) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    missing_required = sorted(REQUIRED_COLUMNS - set(frame.columns))
    if missing_required:
        errors.append(f"Missing required columns: {missing_required}")

    duplicate_rows = int(frame.duplicated().sum())
    if duplicate_rows:
        warnings.append(f"Duplicate complete rows detected: {duplicate_rows}")

    duplicate_periods = 0
    if {"enterprise_id", "month_date"} <= set(frame.columns):
        duplicate_periods = int(frame.duplicated(["enterprise_id", "month_date"]).sum())
        if duplicate_periods:
            errors.append(
                f"Duplicate enterprise-month combinations detected: {duplicate_periods}"
            )

    duplicate_enterprise_codes = _inconsistent_enterprise_identity(frame)
    if duplicate_enterprise_codes:
        errors.append(
            "Enterprise identity is inconsistent across rows: "
            f"{duplicate_enterprise_codes} enterprise IDs"
        )

    missing_summary = {
        str(column): int(count)
        for column, count in frame.isna().sum().items()
        if int(count) > 0
    }
    if missing_summary:
        warnings.append(f"Missing values detected in {len(missing_summary)} columns")

    invalid_sector_values = sorted(
        set(frame.get("sector", pd.Series(dtype=str)).dropna().astype(str))
        - EXPECTED_SECTORS
    )
    if invalid_sector_values:
        errors.append(f"Invalid sector values: {invalid_sector_values}")

    negative_values = {
        column: int((frame[column] < 0).sum())
        for column in NON_NEGATIVE_COLUMNS
        if column in frame.columns
        and pd.api.types.is_numeric_dtype(frame[column])
        and (frame[column] < 0).any()
    }
    if negative_values:
        errors.append(f"Negative values in non-negative columns: {negative_values}")

    invalid_temperature = 0
    if "temperature" in frame.columns:
        invalid_temperature = int(
            ((frame.temperature < -90) | (frame.temperature > 70)).sum()
        )
        if invalid_temperature:
            errors.append(
                f"Impossible temperature values detected: {invalid_temperature}"
            )
    invalid_rainfall = 0
    if "rainfall" in frame.columns:
        invalid_rainfall = int(((frame.rainfall < 0) | (frame.rainfall > 5000)).sum())
        if invalid_rainfall:
            errors.append(f"Impossible rainfall values detected: {invalid_rainfall}")

    invalid_target_columns = sorted(set(TARGET_COLUMNS) - set(frame.columns))
    if invalid_target_columns:
        errors.append(f"Invalid or missing target columns: {invalid_target_columns}")

    unexpected_datatypes = {
        column: str(frame[column].dtype)
        for column in NUMERIC_COLUMNS
        if column in frame.columns and not pd.api.types.is_numeric_dtype(frame[column])
    }
    if unexpected_datatypes:
        errors.append(
            f"Unexpected datatypes in numeric columns: {unexpected_datatypes}"
        )

    continuity = _check_continuity(frame)
    errors.extend(continuity["errors"])
    warnings.extend(continuity["warnings"])

    leakage_candidates = _detect_leakage_candidates(frame)
    report: dict[str, Any] = {
        "passed": not errors,
        "rows": int(len(frame)),
        "columns": int(frame.shape[1]),
        "duplicate_complete_rows": duplicate_rows,
        "duplicate_enterprise_month_rows": duplicate_periods,
        "missing_values": missing_summary,
        "invalid_sector_values": invalid_sector_values,
        "negative_value_counts": negative_values,
        "invalid_temperature_rows": invalid_temperature,
        "invalid_rainfall_rows": invalid_rainfall,
        "invalid_target_columns": invalid_target_columns,
        "unexpected_datatypes": unexpected_datatypes,
        "chronological_order": continuity["chronological_order"],
        "enterprise_history_continuity": continuity["enterprise_history_continuity"],
        "target_leakage_candidates": leakage_candidates,
        "errors": errors,
        "warnings": warnings,
    }
    return ValidationResult(report, tuple(errors), tuple(warnings))


def require_valid(result: ValidationResult) -> None:
    if not result.passed:
        raise DatasetValidationError(
            "Dataset validation failed: " + "; ".join(result.errors)
        )


def assess_feature_quality(
    frame: pd.DataFrame,
    feature_columns: list[str],
    leakage_columns: tuple[str, ...],
) -> dict[str, Any]:
    numeric = frame[feature_columns].select_dtypes(include="number")
    constant_columns = [
        column for column in feature_columns if frame[column].nunique(dropna=False) <= 1
    ]
    near_zero_variance = [
        column
        for column in numeric.columns
        if float(numeric[column].var(ddof=0)) <= 1e-12
        or float(numeric[column].nunique(dropna=True) / max(len(numeric), 1)) < 0.001
    ]
    correlated_pairs: list[dict[str, Any]] = []
    if not numeric.empty:
        correlation = numeric.corr().abs()
        for left_index, left in enumerate(correlation.columns):
            for right in correlation.columns[left_index + 1 :]:
                value = correlation.loc[left, right]
                if pd.notna(value) and float(value) >= 0.98:
                    correlated_pairs.append(
                        {
                            "left": left,
                            "right": right,
                            "absolute_correlation": float(value),
                        }
                    )
    redundant_columns = [
        column
        for index, column in enumerate(feature_columns)
        if any(frame[column].equals(frame[other]) for other in feature_columns[:index])
    ]
    identifier_columns = [
        column for column in feature_columns if column in IDENTIFIER_COLUMNS
    ]
    leakage_candidates = [
        {"column": column, "reason": "excluded from ML features"}
        for column in leakage_columns
        if column in frame.columns
    ]
    return {
        "input_feature_count": len(feature_columns),
        "constant_columns": constant_columns,
        "near_zero_variance_columns": sorted(set(near_zero_variance)),
        "highly_correlated_pairs": correlated_pairs,
        "redundant_columns": redundant_columns,
        "identifier_columns": identifier_columns,
        "potential_leakage_columns": leakage_candidates,
        "usable_feature_count": len(
            [column for column in feature_columns if column not in leakage_columns]
        ),
    }


def _inconsistent_enterprise_identity(frame: pd.DataFrame) -> int:
    if not {"enterprise_id", "enterprise_code"} <= set(frame.columns):
        return 0
    identity_counts = frame.groupby("enterprise_id")["enterprise_code"].nunique(
        dropna=False
    )
    return int((identity_counts > 1).sum())


def _check_continuity(frame: pd.DataFrame) -> dict[str, Any]:
    if not {"enterprise_id", "month_date"} <= set(frame.columns):
        return {
            "errors": [
                "Cannot validate timestamp continuity without enterprise_id/month_date"
            ],
            "warnings": [],
            "chronological_order": False,
            "enterprise_history_continuity": False,
        }
    errors: list[str] = []
    warnings: list[str] = []
    chronological = True
    continuous = True
    for enterprise_id, group in frame.groupby("enterprise_id", sort=False):
        parsed_dates = pd.to_datetime(group["month_date"], errors="coerce")
        if parsed_dates.isna().any():
            continuous = False
            errors.append(f"Enterprise {enterprise_id} has invalid timestamps")
            continue
        dates = parsed_dates.dropna()
        if not dates.is_monotonic_increasing:
            chronological = False
            errors.append(f"Enterprise {enterprise_id} is not chronologically ordered")
        expected = pd.date_range(dates.min(), dates.max(), freq="MS")
        if len(expected) != len(dates) or not dates.reset_index(drop=True).equals(
            pd.Series(expected)
        ):
            continuous = False
            errors.append(
                f"Enterprise {enterprise_id} has discontinuous monthly history"
            )
    if len(errors) > 20:
        warnings.append(
            f"Continuity errors truncated after 20 entries: {len(errors)} total"
        )
        errors = errors[:20]
    return {
        "errors": errors,
        "warnings": warnings,
        "chronological_order": chronological,
        "enterprise_history_continuity": continuous,
    }


def _detect_leakage_candidates(frame: pd.DataFrame) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    for column in frame.columns:
        lowered = column.lower()
        if column in TARGET_COLUMNS or "after_" in lowered:
            candidates.append({"column": column, "reason": "explicit target"})
        elif column in {"risk_factors", "risk_score", "risk_level"}:
            candidates.append(
                {"column": column, "reason": "current outcome or derived label"}
            )
    return candidates
