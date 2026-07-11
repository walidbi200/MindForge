import os
from pydantic import BaseModel, Field

class Settings(BaseModel):
    APP_NAME: str = "MindForge API"
    VERSION: str = "0.0.2"
    ENVIRONMENT: str = Field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    API_HOST: str = Field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))
    API_PORT: int = Field(default_factory=lambda: int(os.getenv("API_PORT", "8000")))
    CORS_ORIGINS: list[str] = ["*"]

settings = Settings()
