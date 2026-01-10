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

    # API
    API_PREFIX: str = "/api/v1"
    API_KEY: str | None = None  # Opcional - solo si necesitas proteger la API

    # App
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
