from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = Field(..., alias="DATABASE_URL")
    jwt_secret: str = Field(..., alias="JWT_SECRET")
    jwt_expires_min: int = Field(60, alias="JWT_EXPIRES_MIN")
    cors_origins: List[str] = Field(default_factory=lambda: ["*"], alias="CORS_ORIGINS")

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


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_database_url() -> str:
    return get_settings().database_url
