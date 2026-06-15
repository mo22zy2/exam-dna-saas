from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:devpassword@localhost:5432/examdna"
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    google_client_id: str = ""
    google_client_secret: str = ""
    jwt_secret: str = "change-me-to-a-random-secret"
    jwt_expiry: int = 604800

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
