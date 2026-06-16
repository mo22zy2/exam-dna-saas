from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:devpassword@localhost:5432/examdna"
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    google_client_id: str = ""
    google_client_secret: str = ""
    jwt_secret: str = "change-me-to-a-random-secret"
    jwt_expiry: int = 604800

    # File upload
    upload_storage_path: str = "uploads"
    max_file_size_mb: int = 50
    max_files_per_batch: int = 10
    free_tier_file_limit: int = 20
    free_tier_analysis_limit: int = 1

    # R2 / S3-compatible storage
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = ""
    r2_endpoint_url: str = ""
    r2_region: str = "auto"

    # Local dev
    app_url: str = "http://localhost:8000"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
