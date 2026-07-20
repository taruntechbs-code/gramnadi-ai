from __future__ import annotations

from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import log_loss

try:
    from sklearn.frozen import FrozenEstimator
except ImportError:  # pragma: no cover - compatibility with older scikit-learn
    FrozenEstimator = None


def calibrate_classifier(model, X_validation, y_validation, label_encoder, method: str):
    encoded = label_encoder.transform(y_validation)
    methods = (
        ["sigmoid", "isotonic"]
        if method == "auto"
        else ["sigmoid" if method == "platt" else method]
    )
    candidates = []
    for candidate in methods:
        if FrozenEstimator is not None:
            calibrated = CalibratedClassifierCV(
                FrozenEstimator(model), method=candidate, cv=None
            )
        else:
            calibrated = CalibratedClassifierCV(model, method=candidate, cv="prefit")
        calibrated.fit(X_validation, encoded)
        score = log_loss(encoded, calibrated.predict_proba(X_validation))
        candidates.append((score, candidate, calibrated))
    _, selected, calibrated = min(candidates, key=lambda item: item[0])
    return calibrated, selected
