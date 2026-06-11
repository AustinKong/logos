from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Logos API"
    environment: str = "development"

    model_config = SettingsConfigDict(env_prefix="API_")


@lru_cache
def get_settings() -> Settings:
    return Settings()
