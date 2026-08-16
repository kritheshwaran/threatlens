from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...crud.scan import get_user_scan, list_user_scans, scan_to_response_dict
from ...database.database import get_db
from ...models.user import User
from ...schemas.scan import ScanHistoryItem, ScanResponse
from ..deps import get_current_user

router = APIRouter()


@router.get('/', response_model=list[ScanHistoryItem])
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_user_scans(db, user_id=current_user.id)


@router.get('/{scan_id}', response_model=ScanResponse)
def get_scan_detail(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scan = get_user_scan(db, user_id=current_user.id, scan_id=scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan_to_response_dict(scan)