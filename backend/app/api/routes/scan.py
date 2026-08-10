from fastapi import APIRouter

router = APIRouter()

@router.get('/')
def get_scan_status():
    return {'status': 'idle'}
