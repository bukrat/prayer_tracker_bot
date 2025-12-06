import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date
import asyncio
from typing import Dict, List, Optional
from config import config
from logger import logger

class SheetsManager:
    def __init__(self):
        self.scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        try:
            self.creds = Credentials.from_service_account_file(
                config.CREDENTIALS_FILE, 
                scopes=self.scope
            )
            self.client = gspread.authorize(self.creds)
            self.sheet = self.client.open_by_key(config.SPREADSHEET_ID)
            logger.info("✅ Google Sheets подключен успешно!")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к Google Sheets: {e}")
            self.sheet = None
    
    async def get_today_prayer_times(self) -> Optional[Dict[str, str]]:
        """Получить времена намаза на сегодня"""
        await asyncio.sleep(0)
        logger.info("📅 Функция get_today_prayer_times в разработке")
        return None
    
    async def log_prayer_notification(self, prayer_name: str, user_id: int):
        """Логировать отправленное уведомление"""
        await asyncio.sleep(0)
        logger.info(f"✅ Уведомление {prayer_name} залогировано")

sheets_manager = SheetsManager()

