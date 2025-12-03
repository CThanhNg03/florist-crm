from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    database_url: str = Field(..., alias="DATABASE_URL")
    jwt_secret: str = Field(..., alias="JWT_SECRET")
    jwt_expires_min: int = Field(60, alias="JWT_EXPIRES_MIN")
    cors_origins: List[str] = Field(default_factory=lambda: ["*"], alias="CORS_ORIGINS")
    media_root: Path = Field(default=Path("media"), alias="MEDIA_ROOT")
    media_url: str = Field(default="/media", alias="MEDIA_URL")

    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "env_prefix": "",
    }

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value: List[str] | str | None) -> List[str]:
        if value is None:
            return ["*"]
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def async_database_url(self) -> str:
        url = make_url(self.database_url)
        if url.drivername.startswith("postgresql+asyncpg"):
            return url.render_as_string(hide_password=False)
        if url.drivername.startswith("postgresql"):
            url = url.set(drivername="postgresql+asyncpg")
        return url.render_as_string(hide_password=False)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.media_root.mkdir(parents=True, exist_ok=True)
    return settings


def get_database_url() -> str:
    return get_settings().database_url


def get_async_database_url() -> str:
    return get_settings().async_database_url
