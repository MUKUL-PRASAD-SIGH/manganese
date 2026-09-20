"""Models are artifacts, not code paths. Retraining never touches the API."""

from functools import lru_cache
from pathlib import Path

import joblib
import shap

from app.core.config import settings


@lru_cache(maxsize=8)
def load(name: str):
    return joblib.load(Path(settings.model_dir) / f"{name}.joblib")


@lru_cache(maxsize=1)
def explainer():
    return shap.TreeExplainer(load("shortfall")["q"][0.5])
