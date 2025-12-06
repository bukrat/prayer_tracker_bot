from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Config(BaseSettings):
    # ============ TELEGRAM ============
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "8234743285:AAGJ3pCwuNBtwKRjVMVnD0jzMX8om8gePhA")
    
    # ============ GOOGLE SHEETS ============
    SPREADSHEET_ID: str = os.getenv("SPREADSHEET_ID", "YOUR_SPREADSHEET_ID")
    CREDENTIALS_FILE: str = "credentials.json"
    
    # ============ PRAYER SETTINGS ============
    PRAYER_NAMES: List[str] = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
    PRAYER_SHEET_NAME: str = "PrayerTimes"
    TRACKING_SHEET_NAME: str = "PrayerTracking"
    
    # ============ TIMEZONE ============
    TIMEZONE: str = "Europe/Moscow"
    
    # ============ LOGGING ============
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

config = Config()

