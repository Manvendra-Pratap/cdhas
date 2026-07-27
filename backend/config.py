import os
from typing import List
from pydantic import BaseModel

class Settings(BaseModel):
    APP_TITLE: str = "CDHAS API"
    APP_DESCRIPTION: str = "Cowrie Data & Honeypot Analytics System REST API for Security Operations Center (SOC) threat telemetry"
    APP_VERSION: str = "1.0.0"
    
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    MONGO_URI: str = os.getenv("CDHAS_MONGO_URI", "mongodb://localhost:27017/")
    DB_NAME: str = os.getenv("CDHAS_DB_NAME", "honeypot")
    COLLECTION_NAME: str = os.getenv("CDHAS_COLLECTION_NAME", "attacks")
    
    LOG_DIR: str = "logs"
    LOG_FILE: str = "logs/cdhas_backend.log"
    LOG_LEVEL: str = os.getenv("CDHAS_LOG_LEVEL", "INFO")

    # Security & JWT Configuration
    JWT_SECRET: str = os.getenv("CDHAS_JWT_SECRET", "cdhas-super-secret-jwt-key-2026-production-secure-98765")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("CDHAS_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("CDHAS_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # Admin Credentials
    ADMIN_USERNAME: str = os.getenv("CDHAS_ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD_HASH: str = os.getenv(
        "CDHAS_ADMIN_PASSWORD_HASH",
        "94a2b97c83f120d64e9185a41c2d0f01:e5a8f092312b9c7d41f0284e91285c1042e91285c1042e91285c1042e91285c10"
    )

    # CORS & Input Constraints
    CORS_ALLOWED_ORIGINS: List[str] = [
        origin.strip() for origin in os.getenv("CDHAS_CORS_ORIGINS", "*").split(",")
    ]
    MAX_REQUEST_SIZE_BYTES: int = int(os.getenv("CDHAS_MAX_REQUEST_SIZE_BYTES", str(10 * 1024 * 1024))) # 10 MB
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("CDHAS_RATE_LIMIT_PER_MINUTE", "120"))

    # Performance Cache TTL
    CACHE_TTL_SECONDS: int = int(os.getenv("CDHAS_CACHE_TTL_SECONDS", "3"))

settings = Settings()
