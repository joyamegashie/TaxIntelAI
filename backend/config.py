import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Database Configuration
    database_url: str = Field(default="sqlite:///./taxintel.db", env="DATABASE_URL")

    # Security Configuration
    secret_key: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    # API Keys
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    sentinel_api_key: str = Field(default="", env="SENTINEL_API_KEY")

    # CORS Configuration
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="ALLOWED_ORIGINS",
    )

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")

    # Encryption
    encryption_key: str = Field(
        default="your-encryption-key-here", env="ENCRYPTION_KEY"
    )

    class Config:
        env_file = ".env"


settings = Settings()
