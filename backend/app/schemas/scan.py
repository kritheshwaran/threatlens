from typing import Literal

from pydantic import BaseModel, Field


class ScanRequest(BaseModel):
    url: str = Field(..., min_length=1, examples=["https://example.com"])


class Factor(BaseModel):
    label: str
    positive: bool


class ScanResponse(BaseModel):
    url: str
    normalized_url: str
    classification: Literal["safe", "suspicious", "malicious"]
    confidence: float
    risk_score: float
    model_name: str
    features: dict
    factors: list[Factor]