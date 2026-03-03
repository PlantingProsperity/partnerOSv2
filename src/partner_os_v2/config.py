"""Runtime configuration for Partner OS v2."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed runtime settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: str = Field(default="dev", alias="PARTNER_OS_V2_ENV")
    database_url: str = Field(default="sqlite:///./partner_os_v2.db", alias="PARTNER_OS_V2_DATABASE_URL")

    token_secret: str = Field(default="change-me", alias="PARTNER_OS_V2_TOKEN_SECRET")
    token_ttl_seconds: int = Field(default=28_800, alias="PARTNER_OS_V2_TOKEN_TTL_SECONDS")

    admin_username: str = Field(default="admin", alias="PARTNER_OS_V2_ADMIN_USERNAME")
    admin_password: str = Field(default="admin123", alias="PARTNER_OS_V2_ADMIN_PASSWORD")

    ai_mode: str = Field(default="gemini", alias="PARTNER_OS_V2_AI_MODE")
    gemini_api_key: str = Field(default="", alias="PARTNER_OS_V2_GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.0-flash", alias="PARTNER_OS_V2_GEMINI_MODEL")
    gemini_timeout_seconds: int = Field(default=20, alias="PARTNER_OS_V2_GEMINI_TIMEOUT_SECONDS")
    require_ai_recommendation: bool = Field(default=True, alias="PARTNER_OS_V2_REQUIRE_AI_RECOMMENDATION")

    smtp_host: str = Field(default="", alias="PARTNER_OS_V2_SMTP_HOST")
    smtp_port: int = Field(default=587, alias="PARTNER_OS_V2_SMTP_PORT")
    smtp_username: str = Field(default="", alias="PARTNER_OS_V2_SMTP_USERNAME")
    smtp_password: str = Field(default="", alias="PARTNER_OS_V2_SMTP_PASSWORD")
    smtp_from: str = Field(default="", alias="PARTNER_OS_V2_SMTP_FROM")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
