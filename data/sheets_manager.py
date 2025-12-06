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
            self._init_sheets()
            logger.info("✅ Google Sheets подключен успешно!")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к Google Sheets: {e}")
            self.sheet = None
    
    def _init_sheets(self):
        """Инициализация листов"""
        try:
            self.prayer_times_ws = self.sheet.worksheet(config.PRAYER_SHEET_NAME)
            logger.info(f"✅ Лист '{config.PRAYER_SHEET_NAME}' найден")
        except gspread.exceptions.WorksheetNotFound:
            logger.info(f"⚠️ Создаю лист '{config.PRAYER_SHEET_NAME}'...")
            self.prayer_times_ws = self.sheet.add_worksheet(
                title=config.PRAYER_SHEET_NAME, 
                rows=365, 
                cols=6
            )
            self._setup_prayer_times_sheet()
        
        try:
            self.tracking_ws = self.sheet.worksheet(config.TRACKING_SHEET_NAME)
            logger.info(f"✅ Лист '{config.TRACKING_SHEET_NAME}' найден")
        except gspread.exceptions.WorksheetNotFound:
            logger.info(f"⚠️ Создаю лист '{config.TRACKING_SHEET_NAME}'...")
            self.tracking_ws = self.sheet.add_worksheet(
                title=config.TRACKING_SHEET_NAME,
                rows=10000,
                cols=6
            )
            self._setup_tracking_sheet()
    
    def _setup_prayer_times_sheet(self):
        """Инициализация PrayerTimes листа"""
        headers = ["Date"] + config.PRAYER_NAMES
        self.prayer_times_ws.insert_row(headers, 1)
        logger.info("✅ PrayerTimes заголовки добавлены")
    
    def _setup_tracking_sheet(self):
        """Инициализация Tracking листа"""
        headers = ["Date", "Time", "Prayer", "Read?", "Timestamp"]
        self.tracking_ws.insert_row(headers, 1)
        logger.info("✅ Tracking заголовки добавлены")
    
    async def get_today_prayer_times(self) -> Optional[Dict[str, str]]:
        """Получить времена намаза на сегодня из Sheets"""
        await asyncio.sleep(0)
        
        if not self.sheet:
            logger.error("❌ Google Sheets не подключен")
            return None
        
        today = date.today().isoformat()
        try:
            # Ищем сегодняшнюю дату в PrayerTimes листе
            cells = self.prayer_times_ws.findall(today)
            
            if not cells:
                logger.warning(f"❌ Нет времен намаза для {today}")
                return None
            
            row_idx = cells[0].row
            row_data = self.prayer_times_ws.row_values(row_idx)
            
            # row_data = ["2025-12-06", "06:15", "12:30", "16:45", "18:04", "19:30"]
            prayer_times = {}
            for i, prayer_name in enumerate(config.PRAYER_NAMES):
                if i + 1 < len(row_data):
                    prayer_times[prayer_name] = row_data[i + 1]
            
            logger.info(f"✅ Времена намаза загружены: {prayer_times}")
            return prayer_times
            
        except Exception as e:
            logger.error(f"❌ Ошибка при загрузке времен: {e}")
            return None
    
    async def log_prayer_notification(
        self,
        prayer_name: str,
        read_status: str = "⏳"
    ):
        """Логировать уведомление о намазе"""
        await asyncio.sleep(0)
        
        if not self.sheet:
            return
        
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        timestamp = now.isoformat()
        
        try:
            self.tracking_ws.append_row([
                date_str,
                time_str,
                prayer_name,
                read_status,
                timestamp
            ])
            logger.info(f"✅ {prayer_name} записан в таблицу")
        except Exception as e:
            logger.error(f"❌ Ошибка логирования: {e}")
    
    async def update_prayer_response(
        self,
        prayer_name: str,
        read_status: str
    ):
        """Обновить ответ пользователя"""
        await asyncio.sleep(0)
        
        if not self.sheet:
            return
        
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        
        try:
            # Ищем последнюю запись с этим намазом в этот день
            cells = self.tracking_ws.findall(prayer_name)
            
            for cell in reversed(cells):
                row_data = self.tracking_ws.row_values(cell.row)
                if len(row_data) > 0 and row_data[0] == date_str:
                    # Обновляем колонку "Read?" (4-я колонка)
                    self.tracking_ws.update_cell(cell.row, 4, read_status)
                    logger.info(f"✅ {prayer_name}: {read_status}")
                    return
            
        except Exception as e:
            logger.error(f"❌ Ошибка обновления: {e}")

sheets_manager = SheetsManager()

