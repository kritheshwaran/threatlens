"""
Reloads the saved model from ml/models/model.joblib and re-evaluates it
on a freshly re-split test set (same random_state as training, so the
split is identical), printing a full classification report.

Run:
    python ml/scripts/evaluate.py
"""

import json
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.services.feature_extractor import FEATURE_NAMES  # noqa: E402

PROCESSED_PATH = PROJECT_ROOT / "ml" / "data" / "processed" / "features.csv"
MODEL_PATH = PROJECT_ROOT / "ml" / "models" / "model.joblib"
METADATA_PATH = PROJECT_ROOT / "ml" / "models" / "metadata.json"


def main():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"{MODEL_PATH} not found. Run ml/scripts/train.py first.")

    with open(METADATA_PATH) as f:
        metadata = json.load(f)

    df = pd.read_csv(PROCESSED_PATH)
    X = df[FEATURE_NAMES]
    y = df["label"]

    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=metadata["random_state"], stratify=y
    )

    model = joblib.load(MODEL_PATH)
    preds = model.predict(X_test)

    print(f"Model: {metadata['model_name']}")
    print(f"Test set size: {len(X_test)}\n")
    print("Classification report:")
    print(classification_report(y_test, preds, target_names=["legitimate", "phishing"]))
    print("Confusion matrix (rows=actual, cols=predicted):")
    print(confusion_matrix(y_test, preds))


if __name__ == "__main__":
    main()