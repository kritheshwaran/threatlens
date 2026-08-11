"""
Reads ml/data/raw/urls.csv (columns: url,label), extracts the canonical
feature vector for every URL using backend.app.services.feature_extractor,
and writes ml/data/processed/features.csv (feature columns + label).

Run:
    python ml/scripts/preprocess.py
"""

import sys
from pathlib import Path

import pandas as pd

# Make the `backend` package importable when running this script directly.
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.services.feature_extractor import FEATURE_NAMES, extract_features  # noqa: E402

RAW_PATH = PROJECT_ROOT / "ml" / "data" / "raw" / "urls.csv"
PROCESSED_PATH = PROJECT_ROOT / "ml" / "data" / "processed" / "features.csv"


def main():
    if not RAW_PATH.exists():
        raise FileNotFoundError(
            f"{RAW_PATH} not found. Run ml/scripts/generate_dataset.py first "
            "(or supply your own urls.csv with `url,label` columns)."
        )

    df = pd.read_csv(RAW_PATH)
    if not {"url", "label"}.issubset(df.columns):
        raise ValueError("urls.csv must have `url` and `label` columns")

    print(f"Extracting features for {len(df)} URLs...")
    feature_rows = [extract_features(u) for u in df["url"]]
    features_df = pd.DataFrame(feature_rows, columns=FEATURE_NAMES)
    features_df["label"] = df["label"].values
    features_df["url"] = df["url"].values

    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    features_df.to_csv(PROCESSED_PATH, index=False)
    print(f"Wrote {len(features_df)} rows to {PROCESSED_PATH}")


if __name__ == "__main__":
    main()