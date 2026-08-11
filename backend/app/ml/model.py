"""
Loads the trained model artifact (ml/models/model.joblib + metadata.json)
and exposes a minimal predict interface. This is intentionally thin --
all feature engineering lives in app.services.feature_extractor, and all
business logic (thresholds, labels) lives in app.ml.predictor.
"""

import json
from pathlib import Path
from threading import Lock

import joblib
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
MODEL_PATH = PROJECT_ROOT / "ml" / "models" / "model.joblib"
METADATA_PATH = PROJECT_ROOT / "ml" / "models" / "metadata.json"


class ModelNotTrainedError(RuntimeError):
    """Raised when model.joblib / metadata.json are missing."""


class ThreatModel:
    """Lazily-loaded singleton wrapper around the trained sklearn model."""

    _instance = None
    _lock = Lock()

    def __init__(self):
        self._model = None
        self._metadata = None
        self._load()

    @classmethod
    def get(cls) -> "ThreatModel":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    def _load(self):
        if not MODEL_PATH.exists() or not METADATA_PATH.exists():
            raise ModelNotTrainedError(
                f"No trained model found at {MODEL_PATH}. "
                "Run: python ml/scripts/generate_dataset.py && "
                "python ml/scripts/preprocess.py && python ml/scripts/train.py"
            )
        self._model = joblib.load(MODEL_PATH)
        with open(METADATA_PATH) as f:
            self._metadata = json.load(f)

    @property
    def feature_names(self):
        return self._metadata["feature_names"]

    @property
    def model_name(self):
        return self._metadata["model_name"]

    @property
    def metrics(self):
        return self._metadata["chosen_metrics"]

    def predict_proba(self, feature_vector: list) -> float:
        """Return probability (0-1) that the URL is phishing (class 1)."""
        row = pd.DataFrame([feature_vector], columns=self.feature_names)
        proba = self._model.predict_proba(row)[0]
        # class order follows the classifier's `classes_`; class 1 = phishing
        classes = list(self._model.classes_)
        phishing_index = classes.index(1)
        return float(proba[phishing_index])