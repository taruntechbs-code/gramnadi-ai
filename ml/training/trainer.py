from __future__ import annotations

from typing import Any

import numpy as np
import optuna
from xgboost import XGBClassifier, XGBRegressor


def tune_regressor(
    X_train, y_train, X_validation, y_validation, config, logger
) -> dict[str, Any]:
    if config.n_trials == 0:
        return {}

    def objective(trial):
        params = {
            "max_depth": trial.suggest_int("max_depth", 3, 9),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.25, log=True),
            "subsample": trial.suggest_float("subsample", 0.65, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.65, 1.0),
            "n_estimators": trial.suggest_int("n_estimators", 100, 500),
            "min_child_weight": trial.suggest_float("min_child_weight", 1, 10),
            "gamma": trial.suggest_float("gamma", 0, 5),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-3, 20, log=True),
        }
        model = XGBRegressor(
            objective="reg:squarederror",
            eval_metric="rmse",
            tree_method="hist",
            random_state=config.random_seed,
            n_jobs=config.n_jobs,
            **params,
        )
        model.fit(
            X_train, y_train, eval_set=[(X_validation, y_validation)], verbose=False
        )
        return float(
            np.sqrt(np.mean((y_validation - model.predict(X_validation)) ** 2))
        )

    study = optuna.create_study(
        direction="minimize",
        sampler=optuna.samplers.TPESampler(seed=config.random_seed),
    )
    study.optimize(objective, n_trials=config.n_trials, show_progress_bar=False)
    logger.info("Regression tuning complete: best RMSE %.4f", study.best_value)
    return study.best_params


def tune_classifier(
    X_train, y_train, X_validation, y_validation, config, logger
) -> dict[str, Any]:
    if config.n_trials == 0:
        return {}

    def objective(trial):
        params = {
            "max_depth": trial.suggest_int("max_depth", 3, 9),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.25, log=True),
            "subsample": trial.suggest_float("subsample", 0.65, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.65, 1.0),
            "n_estimators": trial.suggest_int("n_estimators", 100, 500),
            "min_child_weight": trial.suggest_float("min_child_weight", 1, 10),
            "gamma": trial.suggest_float("gamma", 0, 5),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-3, 20, log=True),
        }
        model = XGBClassifier(
            objective="multi:softprob",
            eval_metric="mlogloss",
            num_class=len(np.unique(y_train)),
            tree_method="hist",
            random_state=config.random_seed,
            n_jobs=config.n_jobs,
            **params,
        )
        model.fit(
            X_train, y_train, eval_set=[(X_validation, y_validation)], verbose=False
        )
        probabilities = model.predict_proba(X_validation)
        return float(
            -np.mean(
                np.log(
                    np.maximum(
                        probabilities[np.arange(len(y_validation)), y_validation], 1e-12
                    )
                )
            )
        )

    study = optuna.create_study(
        direction="minimize",
        sampler=optuna.samplers.TPESampler(seed=config.random_seed),
    )
    study.optimize(objective, n_trials=config.n_trials, show_progress_bar=False)
    logger.info("Classification tuning complete: best log loss %.4f", study.best_value)
    return study.best_params
