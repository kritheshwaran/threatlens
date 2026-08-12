from fastapi import APIRouter, HTTPException

from ...ml.model import ModelNotTrainedError
from ...schemas.scan import ScanRequest, ScanResponse
from ...services.security_report import generate_security_report

router = APIRouter()


@router.get('/')
def get_scan_status():
    return {'status': 'idle'}


@router.post('/', response_model=ScanResponse)
def scan_url(payload: ScanRequest):
    if not payload.url or not payload.url.strip():
        raise HTTPException(status_code=422, detail="url must not be empty")

    try:
        result = generate_security_report(payload.url)
    except ModelNotTrainedError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return result