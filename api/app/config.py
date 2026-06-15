from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:devpassword@localhost:5432/examdna"
    redis_url: str = "redis://localhost:6379/0"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
