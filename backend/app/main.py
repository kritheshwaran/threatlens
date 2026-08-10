from fastapi import FastAPI
from .api.router import api_router

app = FastAPI(title='ThreatLens API')
app.include_router(api_router, prefix='/api')

@app.get('/')
def root():
    return {'message': 'ThreatLens backend is running'}
