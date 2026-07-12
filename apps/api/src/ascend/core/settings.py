import os

from pydantic import BaseModel, Field


class Settings(BaseModel):
    APP_NAME: str = "MindForge API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    API_HOST: str = Field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))
    API_PORT: int = Field(default_factory=lambda: int(os.getenv("API_PORT", "8000")))
    # Comma-separated allowed origins. Set to exact Vercel URL in production; no wildcard.
    CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    )
    DATABASE_URL: str = Field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///mindforge.db"))
    OPENROUTER_API_KEY: str = Field(default_factory=lambda: os.getenv("OPENROUTER_API_KEY", ""))
    OPENROUTER_MODEL: str = Field(default_factory=lambda: os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash"))
    OPENROUTER_BASE_URL: str = Field(
        default_factory=lambda: os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    )
    # Shared secret checked on AI endpoints. Empty = guard disabled (local dev).
    APP_SECRET_KEY: str = Field(default_factory=lambda: os.getenv("APP_SECRET_KEY", ""))
    # Sentry DSN for error tracking. Empty = Sentry disabled.
    SENTRY_DSN: str = Field(default_factory=lambda: os.getenv("SENTRY_DSN", ""))


settings = Settings()
