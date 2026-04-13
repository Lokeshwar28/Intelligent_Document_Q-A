from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "DocQA Platform"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False
    api_prefix: str = "/api/v1"

    # Security
    secret_key: str
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    api_key_header: str = "X-API-Key"

    # Database
    database_url: str  # postgresql+asyncpg://user:pass@host:5432/dbname
    db_pool_size: int = 10
    db_max_overflow: int = 20

    # Redis
    redis_url: str  # redis://localhost:6379/0
    cache_ttl_seconds: int = 3600  # 1 hour

    # Celery
    celery_broker_url: str  # redis://localhost:6379/1
    celery_result_backend: str  # redis://localhost:6379/2

    # AWS
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    s3_bucket_name: str = "docqa-documents"
    aws_endpoint_url: str = ""  # set to http://localhost:4566 for local dev

    # Anthropic
    anthropic_api_key: str
    claude_model: str = "claude-sonnet-4-5"
    claude_max_tokens: int = 4096

    # Voyage AI
    voyage_api_key: str = ""

    # Vector DB (Chroma)
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    chroma_collection_name: str = "documents"

    # Embedding
    embedding_model: str = "voyage-3"  # via Anthropic
    chunk_size: int = 1000
    chunk_overlap: int = 200
    retrieval_top_k: int = 8

    

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()