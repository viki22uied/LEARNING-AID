from pydantic import BaseSettings, Field
from typing import List, Optional
import os


class Settings(BaseSettings):
    # Database
    database_url: str = Field(
        default="postgresql://user:pass@localhost:5432/open_edu_db",
        env="DATABASE_URL"
    )
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    
    # ML Models
    embeddings_model: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDINGS_MODEL")
    stt_model: str = Field(default="whisper-base", env="STT_MODEL")
    vector_db_type: str = Field(default="qdrant", env="VECTOR_DB_TYPE")
    qdrant_url: str = Field(default="http://localhost:6333", env="QDRANT_URL")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_workers: int = Field(default=4, env="API_WORKERS")
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    
    # Content Sources
    wikipedia_api_base: str = Field(
        default="https://en.wikipedia.org/w/api.php",
        env="WIKIPEDIA_API_BASE"
    )
    openstax_api_base: str = Field(
        default="https://openstax.org/api",
        env="OPENSTAX_API_BASE"
    )
    oer_commons_api_key: Optional[str] = Field(default=None, env="OER_COMMONS_API_KEY")
    arxiv_api_base: str = Field(
        default="http://export.arxiv.org/api",
        env="ARXIV_API_BASE"
    )
    youtube_api_key: Optional[str] = Field(default=None, env="YOUTUBE_API_KEY")
    
    # Processing Limits
    max_chunk_size: int = Field(default=1000, env="MAX_CHUNK_SIZE")
    max_file_size_mb: int = Field(default=100, env="MAX_FILE_SIZE_MB")
    harvest_rate_limit: int = Field(default=10, env="HARVEST_RATE_LIMIT")
    max_concurrent_harvests: int = Field(default=5, env="MAX_CONCURRENT_HARVESTS")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    
    # Security (optional)
    jwt_secret_key: Optional[str] = Field(default=None, env="JWT_SECRET_KEY")
    admin_api_key: Optional[str] = Field(default=None, env="ADMIN_API_KEY")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
