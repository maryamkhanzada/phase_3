"""
Configuration management using Pydantic Settings.
Loads and validates environment variables from .env file.
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    database_url: str = Field(..., description="PostgreSQL connection string")

    # JWT Configuration
    better_auth_secret: str = Field(..., min_length=32, description="Secret key for JWT signing (min 32 chars)")
    jwt_expiration_hours: int = Field(default=24, description="JWT token expiration time in hours")

    # CORS Configuration
    frontend_url: str = Field(default="http://localhost:3000", description="Frontend origin for CORS")

    # Application Configuration
    app_env: str = Field(default="development", description="Application environment")
    log_level: str = Field(default="INFO", description="Logging level")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
