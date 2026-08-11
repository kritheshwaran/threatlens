"""
Trains phishing-URL classifiers on ml/data/processed/features.csv,
evaluates them, and saves the best-performing model to ml/models/.

Trains two candidate models:
    - Logistic Regression (with StandardScaler, in a Pipeline)
    - Random Forest

Selects the one with the higher F1 score on the held-out test split
and saves it as ml/models/model.joblib, alongside ml/models/metadata.json
containing feature names, chosen model name, and evaluation metrics.

Run:
    python ml/scripts/train.py
"""

import json
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.services.feature_extractor import FEATURE_NAMES  # noqa: E402

PROCESSED_PATH = PROJECT_ROOT / "ml" / "data" / "processed" / "features.csv"
MODELS_DIR = PROJECT_ROOT / "ml" / "models"
MODEL_PATH = MODELS_DIR / "model.joblib"
METADATA_PATH = MODELS_DIR / "metadata.json"

RANDOM_STATE = 42


def evaluate(model, X_test, y_test) -> dict:
    preds = model.predict(X_test)
    return {
        "accuracy": round(accuracy_score(y_test, preds), 4),
        "precision": round(precision_score(y_test, preds), 4),
        "recall": round(recall_score(y_test, preds), 4),
        "f1": round(f1_score(y_test, preds), 4),
    }


def main():
    if not PROCESSED_PATH.exists():
        raise FileNotFoundError(
            f"{PROCESSED_PATH} not found. Run ml/scripts/preprocess.py first."
        )

    df = pd.read_csv(PROCESSED_PATH)
    X = df[FEATURE_NAMES]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    candidates = {
        "logistic_regression": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)),
        ]),
        "random_forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }

    results = {}
    fitted = {}
    for name, model in candidates.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        metrics = evaluate(model, X_test, y_test)
        results[name] = metrics
        fitted[name] = model
        print(f"  {name}: {metrics}")

    best_name = max(results, key=lambda n: results[n]["f1"])
    best_model = fitted[best_name]
    print(f"\nBest model: {best_name} (F1={results[best_name]['f1']})")

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, MODEL_PATH)

    metadata = {
        "model_name": best_name,
        "feature_names": FEATURE_NAMES,
        "metrics": results,
        "chosen_metrics": results[best_name],
        "train_size": len(X_train),
        "test_size": len(X_test),
        "random_state": RANDOM_STATE,
    }
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nSaved model to {MODEL_PATH}")
    print(f"Saved metadata to {METADATA_PATH}")


if __name__ == "__main__":
    main()