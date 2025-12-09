from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    # Откуда читать переменные
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ========= TELEGRAM =========
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_ADMIN_ID: int

    # ========= GOOGLE SHEETS =========
    GOOGLE_SHEET_ID: str
    GOOGLE_CREDENTIALS_FILE: str = "credentials.json"

    # ========= DATABASE =========
    DATABASE_URL: str = "sqlite:///prayer_bot.db"

    # ========= LOGGING =========
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # ========= SCHEDULER =========
    SCHEDULER_ENABLED: bool = True
    SCHEDULER_TIMEZONE: str = "Europe/Moscow"

    # ========= PRAYER TIMES =========
    PRAYER_TIMES_SOURCE: str = "google_sheets"
    PRAYER_NOTIFICATION_MINUTES_BEFORE: int = 5

    # ========= ENVIRONMENT =========
    ENVIRONMENT: str = "production"
    DEBUG: bool = False


# Глобальный экземпляр конфига
config = Config()
