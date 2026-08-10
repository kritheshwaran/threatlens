from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = 'ThreatLens'
    database_url: str = 'sqlite:///./backend/dev.db'

    class Config:
        env_file = '.env'

settings = Settings()
