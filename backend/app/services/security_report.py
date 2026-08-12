"""
Final security report assembly (Module 4): combines the Module 2/3
pipeline (ML prediction + URL/domain/DNS/SSL analysis) with threat
intelligence and the centralized risk engine into the final structured
report returned by POST /scan.

    URL
     -> predict_url()            (Module 2/3: ML + url/domain/dns/ssl)
     -> analyze_threat_intelligence()  (Module 4)
     -> assess_risk()            (Module 4: combines everything)
     -> explain()                (Module 4: reasons for the score)
     -> final structured report
"""

from ..ml.predictor import predict_url
from .threat_intelligence import analyze_threat_intelligence
from .risk_engine import assess_risk
from .explanation import explain


def generate_security_report(url: str) -> dict:
    pipeline_result = predict_url(url)

    hostname = pipeline_result["domain_intelligence"]["hostname"]
    dns_intelligence = pipeline_result["dns_intelligence"]
    ssl_intelligence = pipeline_result["ssl_intelligence"]
    domain_intelligence = pipeline_result["domain_intelligence"]
    factors = pipeline_result["factors"]
    ml_confidence = pipeline_result["confidence"]

    threat_intelligence = analyze_threat_intelligence(
        url=pipeline_result["normalized_url"],
        hostname=hostname,
        dns_intelligence=dns_intelligence,
    )

    risk = assess_risk(
        ml_confidence=ml_confidence,
        factors=factors,
        domain_intelligence=domain_intelligence,
        dns_intelligence=dns_intelligence,
        ssl_intelligence=ssl_intelligence,
        threat_intelligence=threat_intelligence,
    )

    explanation = explain(
        ml_confidence=ml_confidence,
        factors=factors,
        domain_intelligence=domain_intelligence,
        dns_intelligence=dns_intelligence,
        ssl_intelligence=ssl_intelligence,
        threat_intelligence=threat_intelligence,
    )

    return {
        "url": pipeline_result["url"],
        "normalized_url": pipeline_result["normalized_url"],
        "risk_score": risk["risk_score"],
        "classification": risk["classification"],
        "confidence": risk["confidence"],
        "reasons": explanation["reasons"],
        "positive_signals": explanation["positive_signals"],
        "negative_signals": explanation["negative_signals"],
        "url_analysis": {
            "ml_model": pipeline_result["model_name"],
            "ml_phishing_probability": ml_confidence,
            "features": pipeline_result["features"],
            "factors": factors,
        },
        "domain_analysis": domain_intelligence,
        "dns_analysis": dns_intelligence,
        "ssl_analysis": ssl_intelligence,
        "threat_intelligence": threat_intelligence,
        "risk_breakdown": {
            "sub_scores": risk["sub_scores"],
            "weights": risk["weights"],
        },
    }