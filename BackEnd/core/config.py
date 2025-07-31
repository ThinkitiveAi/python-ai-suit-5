"""
Core configuration settings for the FastAPI application.
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings and environment variables."""
    
    # Application settings
    APP_NAME: str = "Provider Registration API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    BCRYPT_ROUNDS: int = 12
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./providers.db")
    MONGODB_URL: Optional[str] = os.getenv("MONGODB_URL")
    DATABASE_TYPE: str = os.getenv("DATABASE_TYPE", "sqlite")  # sqlite, postgresql, mongodb
    
    # Rate limiting settings
    RATE_LIMIT_REQUESTS: int = 5
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour in seconds
    
    # Email settings
    SMTP_HOST: str = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "True").lower() == "true"
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@example.com")
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Timezone
    TIMEZONE: str = "UTC"
    
    # Validation settings
    ALLOWED_SPECIALIZATIONS: List[str] = [
        "Cardiology",
        "Neurology", 
        "Orthopedics",
        "Pediatrics",
        "Dermatology",
        "Psychiatry",
        "Radiology",
        "Anesthesiology",
        "Emergency Medicine",
        "Internal Medicine",
        "Surgery",
        "Obstetrics and Gynecology"
    ]
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        if v == "your-secret-key-change-in-production":
            raise ValueError("Please change the SECRET_KEY in production")
        return v
    
    class Config:
        case_sensitive = True


# Global settings instance
settings = Settings()
