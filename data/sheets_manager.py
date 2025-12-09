"""
Менеджер Google Sheets - управляет доступом и операциями с таблицами
"""
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.auth.exceptions import GoogleAuthError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from config import config
from logger import setup_logger

logger = setup_logger(__name__)

class SheetsManager:
    """Менеджер для работы с Google Sheets"""
    
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    
    def __init__(self):
        """Инициализация менеджера Sheets"""
        self.service = None
        self.spreadsheet_id = config.GOOGLE_SHEET_ID
        self._authenticate()
    
    def _authenticate(self):
        """Аутентификация с Google API"""
        try:
            # Загружаем сервис-аккаунт из JSON
            credentials = service_account.Credentials.from_service_account_file(
                config.GOOGLE_CREDENTIALS_FILE,
                scopes=self.SCOPES
            )
            self.service = build("sheets", "v4", credentials=credentials)
            logger.info("✅ Google Sheets аутентификация успешна")
        except GoogleAuthError as e:
            logger.error(f"❌ Ошибка аутентификации Google: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка при аутентификации: {e}")
            raise
    
    def get_values(self, range_name: str) -> Optional[List[List[str]]]:
        """Получить значения из диапазона"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get("values", [])
            logger.info(f"✅ Получены значения из {range_name}")
            return values
        except HttpError as e:
            logger.error(f"❌ Ошибка HTTP при чтении Sheets: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка при чтении Sheets: {e}")
            return None
    
    def update_values(self, range_name: str, values: List[List[str]]) -> bool:
        """Обновить значения в диапазоне"""
        try:
            body = {"values": values}
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body=body
            ).execute()
            
            logger.info(f"✅ Обновлены {result.get('updatedCells')} ячеек в {range_name}")
            return True
        except HttpError as e:
            logger.error(f"❌ Ошибка HTTP при записи в Sheets: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка при записи в Sheets: {e}")
            return False
    
    def append_values(self, range_name: str, values: List[List[str]]) -> bool:
        """Добавить значения в конец диапазона"""
        try:
            body = {"values": values}
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body=body
            ).execute()
            
            logger.info(f"✅ Добавлены {result.get('updates').get('updatedRows')} строк в {range_name}")
            return True
        except HttpError as e:
            logger.error(f"❌ Ошибка HTTP при добавлении в Sheets: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка при добавлении в Sheets: {e}")
            return False
    
    def clear_range(self, range_name: str) -> bool:
        """Очистить диапазон"""
        try:
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            logger.info(f"✅ Диапазон {range_name} очищен")
            return True
        except HttpError as e:
            logger.error(f"❌ Ошибка HTTP при очистке Sheets: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка при очистке Sheets: {e}")
            return False
    
    def batch_update(self, requests: List[Dict[str, Any]]) -> bool:
        """Пакетное обновление таблицы"""
        try:
            body = {"requests": requests}
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=body
            ).execute()
            
            logger.info(f"✅ Выполнено {len(requests)} пакетных операций")
            return True
        except HttpError as e:
            logger.error(f"❌ Ошибка HTTP при пакетном обновлении: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка при пакетном обновлении: {e}")
            return False

# ✅ Глобальный экземпляр
sheets_manager = SheetsManager()
