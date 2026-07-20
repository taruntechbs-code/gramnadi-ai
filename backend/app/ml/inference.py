from __future__ import annotations

from .loader import ModelLoader
from .predictor import Predictor


def build_predictor(loader: ModelLoader) -> Predictor:
    return Predictor(loader.require_loaded(), loader.config)
