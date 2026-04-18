"""
Application configuration using Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Neon PostgreSQL
    DATABASE_URL: str = ""          # postgresql+asyncpg://user:pass@host/db

    # Groq API
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # JWT Auth
    JWT_SECRET_KEY: str = "change-this-to-a-long-random-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7   # 7 days

    # Frontend URL (for CORS)
    FRONTEND_URL: str = "http://localhost:5173"

    # Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # LLM Settings
    MAX_TOKENS: int = 2048
    TEMPERATURE: float = 0.7
    FAQ_CONFIDENCE_THRESHOLD: float = 0.01

    # Upload Settings
    MAX_FILE_SIZE_MB: int = 10
    ENABLE_USER_FILE_UPLOADS: bool = False

    # FAQ dataset training (server-side)
    FAQ_DATASET_PATH: str = "backend/data/faq_dataset.json"
    ENABLE_INTENT_ROUTER: bool = False
    INTENT_MODEL_PATH: str = "backend/models/intent_router.joblib"
    INTENT_CONFIDENCE_THRESHOLD: float = 0.65

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
