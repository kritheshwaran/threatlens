from fastapi import APIRouter
from .routes import scan, auth, history, analytics

api_router = APIRouter()
api_router.include_router(scan.router, prefix='/scan', tags=['scan'])
api_router.include_router(auth.router, prefix='/auth', tags=['auth'])
api_router.include_router(history.router, prefix='/history', tags=['history'])
api_router.include_router(analytics.router, prefix='/analytics', tags=['analytics'])
