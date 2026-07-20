from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap


def generate_shap_explanations(
    model, X: pd.DataFrame, output_dir: Path, sample_size: int, seed: int
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    sample = X.sample(min(sample_size, len(X)), random_state=seed)
    explainer = shap.TreeExplainer(model)
    values = explainer.shap_values(sample)
    if isinstance(values, list):
        values_for_importance = np.mean(np.abs(np.stack(values)), axis=0)
        summary_values = values[0]
    else:
        values_for_importance = np.abs(values)
        summary_values = values
    importance = pd.DataFrame(
        {
            "feature": sample.columns,
            "mean_abs_shap": np.mean(values_for_importance, axis=0),
        }
    )
    importance.sort_values("mean_abs_shap", ascending=False).to_csv(
        output_dir / "feature_importance.csv", index=False
    )
    shap.summary_plot(summary_values, sample, show=False, max_display=25)
    plt.tight_layout()
    plt.savefig(output_dir / "shap_summary.png", dpi=140, bbox_inches="tight")
    plt.close()
    shap.summary_plot(
        summary_values, sample, plot_type="bar", show=False, max_display=25
    )
    plt.tight_layout()
    plt.savefig(output_dir / "shap_bar.png", dpi=140, bbox_inches="tight")
    plt.close()
    if len(importance):
        feature = importance.iloc[0]["feature"]
        shap.dependence_plot(feature, summary_values, sample, show=False)
        plt.tight_layout()
        plt.savefig(output_dir / "shap_dependence_top_feature.png", dpi=140)
        plt.close()
        expected_value = explainer.expected_value
        if isinstance(expected_value, (list, np.ndarray)):
            expected_value = expected_value[0]
        shap.waterfall_plot(
            shap.Explanation(
                values=summary_values[0],
                base_values=expected_value,
                data=sample.iloc[0],
                feature_names=sample.columns,
            ),
            show=False,
            max_display=15,
        )
        plt.tight_layout()
        plt.savefig(output_dir / "shap_waterfall.png", dpi=140, bbox_inches="tight")
        plt.close()
    return {"sample_rows": len(sample), "feature_count": sample.shape[1]}
