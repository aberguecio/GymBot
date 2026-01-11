from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # Telegram
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_WEBHOOK_URL: str | None = None  # None = modo polling
    TELEGRAM_WEBHOOK_PATH: str = "/webhook/telegram"
    TELEGRAM_USE_POLLING: bool = False  # True = modo polling para desarrollo local

    # Database
    DATABASE_URL: str

    # App
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # Ignorar variables extra del .env
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
