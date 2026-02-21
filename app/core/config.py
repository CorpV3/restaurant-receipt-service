from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    HOST: str = "0.0.0.0"
    PORT: int = 8011
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/receipts"

    class Config:
        env_file = ".env"


settings = Settings()
