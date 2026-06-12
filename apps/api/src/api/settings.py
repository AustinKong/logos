from functools import lru_cache

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AIAPIKeySettings(BaseModel):
    openai: str | None = None
    anthropic: str | None = None
    gemini: str | None = None
    deepseek: str | None = None


class AISettings(BaseModel):
    api_keys: AIAPIKeySettings = Field(default_factory=AIAPIKeySettings)


class Settings(BaseSettings):
    app_name: str = "Logos API"
    environment: str = "development"
    database_url: str = "sqlite:///./logos.db"
    ai: AISettings = Field(default_factory=AISettings)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", env_nested_delimiter="__")


@lru_cache
def get_settings() -> Settings:
    return Settings()
