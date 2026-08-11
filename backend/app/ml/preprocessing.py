"""
Thin convenience wrapper kept for backward compatibility with the
original scaffold. Feature extraction itself lives in
app.services.feature_extractor (the single source of truth used by
both training and serving) -- this module just re-exposes it under
the `app.ml` namespace for callers that expect it here.
"""

from ..services.feature_extractor import (  # noqa: F401
    FEATURE_NAMES,
    extract_features,
    extract_features_dict,
    extract_raw_features,
)


def prepare_features(url: str) -> list:
    """Return the ordered numeric feature vector for a URL."""
    return extract_features(url)