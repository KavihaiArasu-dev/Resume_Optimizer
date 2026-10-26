"""
Resume Optimizer — Backend Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Resume Optimizer"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_PREFIX: str = "/api"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/resume_optimizer"
    DATABASE_SYNC_URL: str = "postgresql://postgres:postgres@localhost:5432/resume_optimizer"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT Auth
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # OpenAI / LLM
    OPENAI_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4o"

    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 10

    # Scoring Weights (configurable as per blueprint)
    WEIGHT_REQUIRED_SKILLS: float = 0.30
    WEIGHT_SEMANTIC_SIMILARITY: float = 0.20
    WEIGHT_EXPERIENCE_ALIGNMENT: float = 0.15
    WEIGHT_RESPONSIBILITIES: float = 0.10
    WEIGHT_KEYWORDS: float = 0.10
    WEIGHT_EDUCATION: float = 0.10
    WEIGHT_PREFERRED_SKILLS: float = 0.05

    # CORS
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
