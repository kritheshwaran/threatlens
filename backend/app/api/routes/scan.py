from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...crud.scan import save_scan, scan_to_response_dict
from ...database.database import get_db
from ...ml.model import ModelNotTrainedError
from ...models.user import User
from ...schemas.scan import ScanRequest, ScanResponse
from ...services.security_report import generate_security_report
from ..deps import get_current_user

router = APIRouter()


@router.get('/')
def get_scan_status():
    return {'status': 'idle'}


@router.post('/', response_model=ScanResponse)
def scan_url(
    payload: ScanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not payload.url or not payload.url.strip():
        raise HTTPException(status_code=422, detail="url must not be empty")

    try:
        report = generate_security_report(payload.url)
    except ModelNotTrainedError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    scan = save_scan(db, user_id=current_user.id, report=report)
    return scan_to_response_dict(scan)