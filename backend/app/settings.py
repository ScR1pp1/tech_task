from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    llm_api_key: str | None = None
    llm_api_base: str | None = None
    llm_model: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    s3_endpoint: str
    s3_access_key: str
    s3_secret_key: str
    s3_bucket: str
    api_key: str = "dev-secret-key"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

