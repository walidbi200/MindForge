import os

from pydantic import BaseModel, Field


class Settings(BaseModel):
    APP_NAME: str = "MindForge API"
    VERSION: str = "0.0.5"
    ENVIRONMENT: str = Field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    API_HOST: str = Field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))
    API_PORT: int = Field(default_factory=lambda: int(os.getenv("API_PORT", "8000")))
    CORS_ORIGINS: list[str] = ["*"]
    DATABASE_URL: str = Field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///mindforge.db"))
    OPENROUTER_API_KEY: str = Field(default_factory=lambda: os.getenv("OPENROUTER_API_KEY", ""))
    OPENROUTER_MODEL: str = Field(default_factory=lambda: os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash"))
    OPENROUTER_BASE_URL: str = Field(
        default_factory=lambda: os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    )


settings = Settings()
