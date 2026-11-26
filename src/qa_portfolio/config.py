"""Environment configuration, validated once at import time.

Values come from the process environment first and `.env` second, so CI only
ever needs repository secrets while a developer can keep a local file. A typo
in a URL or an unsupported log level fails with a readable, field-level message
instead of surfacing later as a confusing timeout.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated runtime settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    base_url: str = "https://www.saucedemo.com"
    api_base_url: str = "https://restful-booker.herokuapp.com"

    sauce_username: str = "standard_user"
    sauce_password: str = "secret_sauce"

    booker_username: str = "admin"
    booker_password: str = "password123"

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    request_timeout: float = Field(default=15.0, gt=0, le=120)

    @field_validator("base_url", "api_base_url")
    @classmethod
    def _require_absolute_http_url(cls, value: str) -> str:
        candidate = value.strip().rstrip("/")
        if not candidate.startswith(("http://", "https://")):
            raise ValueError("must be an absolute http(s) URL, e.g. https://example.com")
        return candidate


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide settings instance.

    Cached so that every module sees one validated object, while tests can
    still call `get_settings.cache_clear()` when they need a fresh read.
    """

    return Settings()
