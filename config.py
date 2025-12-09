"""
Конфигурация для Prayer Tracker Bot
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field

class Config(BaseSettings):
    # ============ TELEGRAM ============
    bot_token: str = Field(
        default="8234743285:AAGJ3pCwuNBtwKRjVMVnD0jzMX8om8gePhA",
        alias="BOT_TOKEN"
    )
    
    # ============ GOOGLE SHEETS ============
    spreadsheet_id: str = Field(
        default="1DhG3PolBXO9BOc6bUDIQqc7f75nIZPt15i2X7U9tO1U",
        alias="SPREADSHEET_ID"
    )
    
    spreadsheet_name: str = "Tracker bot"
    
    credentials_file: str = Field(
        default="credentials.json",
        alias="CREDENTIALS_FILE"
    )
    
    # ============ PRAYER SETTINGS ============
    prayer_names: List[str] = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
    
    # ============ LOGGING ============
    log_level: str = Field(
        default="INFO",
        alias="LOG_LEVEL"
    )
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True  # ✅ Принимаем оба варианта имён
    )
    
    # ✅ PROPERTIES для обратной совместимости
    @property
    def sheets_id(self) -> str:
        return self.spreadsheet_id
    
    @property
    def BOT_TOKEN(self) -> str:
        return self.bot_token

config = Config()
