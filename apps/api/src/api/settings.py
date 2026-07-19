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
    embedding_model: str = "openai/text-embedding-3-small"


class VectorSettings(BaseModel):
    uri: str = "./lancedb"


class Settings(BaseSettings):
    app_name: str = "Logos API"
    environment: str = "development"
    # TODO: Move this to DatabaseSettings
    database_url: str = "sqlite+aiosqlite:///./logos.db"
    ai: AISettings = Field(default_factory=AISettings)
    vector: VectorSettings = Field(default_factory=VectorSettings)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", env_nested_delimiter="__")


@lru_cache
def get_settings() -> Settings:
    return Settings()
