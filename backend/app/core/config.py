"""
Central application configuration. All values are read from
environment variables (via a .env file in development); nothing
sensitive has a real default baked in -- see .env.example at the
project root for the full list of variables to set.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ThreatLens"

    # Database -- PostgreSQL in production. Example:
    #   postgresql+psycopg2://threatlens:password@localhost:5432/threatlens
    database_url: str = "postgresql+psycopg2://threatlens:threatlens@localhost:5432/threatlens"

    # JWT auth
    jwt_secret_key: str = "change-this-secret-in-your-.env-file"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60 * 24  # 24 hours

    # CORS -- comma-separated list of allowed origins
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()