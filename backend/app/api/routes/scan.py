from fastapi import APIRouter, HTTPException

from ...ml.model import ModelNotTrainedError
from ...ml.predictor import predict_url
from ...schemas.scan import ScanRequest, ScanResponse

router = APIRouter()


@router.get('/')
def get_scan_status():
    return {'status': 'idle'}


@router.post('/', response_model=ScanResponse)
def scan_url(payload: ScanRequest):
    if not payload.url or not payload.url.strip():
        raise HTTPException(status_code=422, detail="url must not be empty")

    try:
        result = predict_url(payload.url)
    except ModelNotTrainedError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return result