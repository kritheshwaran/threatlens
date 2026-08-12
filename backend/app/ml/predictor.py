"""
High-level prediction orchestration: URL -> features -> model -> verdict.

This is the module POST /scan calls. It combines:
    - app.services.url_analyzer   (human-readable factors)
    - app.services.feature_extractor (numeric feature vector)
    - app.ml.model.ThreatModel    (trained classifier)

into a single response payload.
"""

from .model import ThreatModel
from ..services.feature_extractor import extract_features, extract_features_dict
from ..services.url_analyzer import analyze_url
from ..services.domain_analyzer import analyze_domain
from ..services.dns_analyzer import analyze_dns
from ..services.ssl_analyzer import analyze_ssl

# Same thresholds used by the Module 1 frontend (frontend/src/utils/risk.js),
# kept in sync intentionally so backend and frontend never disagree on a verdict.
MALICIOUS_THRESHOLD = 70
SUSPICIOUS_THRESHOLD = 35


def _level_from_score(score: float) -> str:
    if score >= MALICIOUS_THRESHOLD:
        return "malicious"
    if score >= SUSPICIOUS_THRESHOLD:
        return "suspicious"
    return "safe"


def predict_url(url: str) -> dict:
    """
    Run the full pipeline for a single URL and return a JSON-serializable
    dict shaped for the /scan API response.

    Note: classification/confidence/risk_score come from the ML model
    ONLY (Module 2). Domain/DNS/SSL intelligence (Module 3) is returned
    alongside it as additional structured context -- it is not yet
    blended into the score. That combination is the final risk engine,
    which is a later module.
    """
    analysis = analyze_url(url)
    feature_vector = extract_features(url)
    features_dict = extract_features_dict(url)

    model = ThreatModel.get()
    phishing_probability = model.predict_proba(feature_vector)
    risk_score = round(phishing_probability * 100, 2)
    level = _level_from_score(risk_score)

    hostname = analysis["hostname"]

    domain_intelligence = analyze_domain(url)
    dns_intelligence = analyze_dns(hostname)
    ssl_intelligence = analyze_ssl(hostname)

    return {
        "url": url,
        "normalized_url": analysis["normalized_url"],
        "classification": level,
        "confidence": round(phishing_probability, 4),
        "risk_score": risk_score,
        "model_name": model.model_name,
        "features": features_dict,
        "factors": analysis["factors"],
        "domain_intelligence": domain_intelligence,
        "dns_intelligence": dns_intelligence,
        "ssl_intelligence": ssl_intelligence,
    }