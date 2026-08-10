from pydantic import BaseModel

class ScanRequest(BaseModel):
    url: str

class ScanResponse(BaseModel):
    url: str
    risk_score: float
    details: dict
