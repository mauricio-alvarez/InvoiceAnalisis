"""Application configuration management"""
import os
from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # GCP Configuration
    gcp_project_id: str
    gcp_region: str = "us-central1"
    
    # Firebase Configuration
    firebase_service_account_path: str = ""
    firebase_service_account_secret: str = ""
    
    # Cloud Storage
    storage_bucket_name: str
    
    # Firestore
    firestore_database: str = "(default)"
    
    # Application Configuration
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    
    # File Upload Limits
    max_file_size_mb: int = 10
    allowed_file_types: str = "application/pdf"
    
    # Security
    signed_url_expiration_hours: int = 1
    
    @property
    def cors_origins_list(self) -> List[str]:
        if not self.cors_origins:
            return []
        # Split the string by comma and strip any whitespace
        return [origin.strip() for origin in self.cors_origins.split(',')]
    
    @property
    def max_file_size_bytes(self) -> int:
        """Convert max file size to bytes"""
        return self.max_file_size_mb * 1024 * 1024
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment.lower() == "production"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
