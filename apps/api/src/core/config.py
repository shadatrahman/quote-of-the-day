"""
Application configuration settings using Pydantic Settings.
Loads configuration from environment variables with validation.
"""

from typing import List, Optional, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    # General Configuration
    ENVIRONMENT: str = Field(default="development", description="Environment name")
    DEBUG: bool = Field(default=True, description="Debug mode")
    LOG_LEVEL: str = Field(default="info", description="Logging level")

    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", description="API host")
    API_PORT: int = Field(default=8000, description="API port")
    SECRET_KEY: str = Field(..., description="JWT secret key")
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Token expiration")

    # Database Configuration
    DATABASE_URL: str = Field(..., description="PostgreSQL database URL")
    DATABASE_POOL_SIZE: int = Field(default=10, description="Database pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, description="Database max overflow")

    # Redis Configuration
    REDIS_URL: str = Field(..., description="Redis URL")

    # CORS and Security
    ALLOWED_ORIGINS: Union[List[str], str] = Field(
        default=["http://localhost:3000"], description="Allowed CORS origins"
    )
    ALLOWED_HOSTS: Union[List[str], str] = Field(
        default=["localhost", "test", "testserver"], description="Allowed hosts"
    )

    # Firebase Configuration
    FIREBASE_PROJECT_ID: Optional[str] = Field(
        default=None, description="Firebase project ID"
    )
    FIREBASE_ADMIN_CREDENTIALS_PATH: Optional[str] = Field(
        default=None, description="Firebase admin credentials path"
    )
    FCM_SERVER_KEY: Optional[str] = Field(default=None, description="FCM server key")

    # AWS Configuration
    AWS_REGION: str = Field(default="us-east-1", description="AWS region")
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, description="AWS access key")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(
        default=None, description="AWS secret key"
    )
    AWS_S3_BUCKET: Optional[str] = Field(default=None, description="S3 bucket name")

    # Email Configuration
    SES_EMAIL_FROM: Optional[str] = Field(default=None, description="SES from email")
    SES_REGION: str = Field(default="us-east-1", description="SES region")

    # Stripe Configuration
    STRIPE_SECRET_KEY: Optional[str] = Field(
        default=None, description="Stripe secret key"
    )
    STRIPE_PUBLISHABLE_KEY: Optional[str] = Field(
        default=None, description="Stripe publishable key"
    )
    STRIPE_WEBHOOK_SECRET: Optional[str] = Field(
        default=None, description="Stripe webhook secret"
    )
    STRIPE_PRICE_ID_PREMIUM: Optional[str] = Field(
        default=None, description="Stripe price ID for premium subscription"
    )

    # Monitoring
    SENTRY_DSN: Optional[str] = Field(default=None, description="Sentry DSN")
    CLOUDWATCH_LOG_GROUP: Optional[str] = Field(
        default=None, description="CloudWatch log group"
    )

    # Development Features
    ENABLE_SWAGGER_UI: bool = Field(default=True, description="Enable Swagger UI")
    ENABLE_REDOC: bool = Field(default=True, description="Enable ReDoc")

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            # Handle both comma-separated strings and JSON arrays
            if v.startswith("[") and v.endswith("]"):
                import json

                return json.loads(v)
            else:
                return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, v):
        """Parse allowed hosts from string or list."""
        if isinstance(v, str):
            # Handle both comma-separated strings and JSON arrays
            if v.startswith("[") and v.endswith("]"):
                import json

                return json.loads(v)
            else:
                return [host.strip() for host in v.split(",")]
        return v

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for Alembic."""
        return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")


# Create global settings instance
settings = Settings()
