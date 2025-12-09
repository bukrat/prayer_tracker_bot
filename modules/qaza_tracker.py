"""
Трекер Каза (пропущенные молитвы) - отслеживание и управление компенсацией
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

from config import config
from logger import setup_logger
from data.sheets_manager import sheets_manager
from utils.time_utils import time_utils

logger = setup_logger(__name__)

class QazaTracker:
    """Трекер для управления пропущенными молитвами"""
    
    # Коды молитв
    PRAYER_CODES = {
        "Fajr": "F",
        "Dhuhr": "D",
        "Asr": "A",
        "Maghrib": "M",
        "Isha": "I"
    }
    
    SHEET_RANGE = "Qaza!A:F"
    
    def __init__(self):
        """Инициализация трекера Каза"""
        self.sheet_manager = sheets_manager
    
    def get_qaza_count(self, user_id: int) -> Dict[str, int]:
        """Получить количество Каза молитв для пользователя"""
        try:
            values = self.sheet_manager.get_values(self.SHEET_RANGE)
            
            if not values:
                logger.warning(f"⚠️ Нет данных Каза для пользователя {user_id}")
                return {prayer: 0 for prayer in self.PRAYER_CODES.keys()}
            
            # Ищем строку пользователя
            for row in values[1:]:  # Пропускаем заголовок
                if row and int(row[0]) == user_id:
                    return {
                        "Fajr": int(row[1]) if len(row) > 1 else 0,
                        "Dhuhr": int(row[2]) if len(row) > 2 else 0,
                        "Asr": int(row[3]) if len(row) > 3 else 0,
                        "Maghrib": int(row[4]) if len(row) > 4 else 0,
                        "Isha": int(row[5]) if len(row) > 5 else 0,
                    }
            
            logger.info(f"ℹ️ Пользователь {user_id} не найден в Каза, создаем новую запись")
            return {prayer: 0 for prayer in self.PRAYER_CODES.keys()}
        except Exception as e:
            logger.error(f"❌ Ошибка при получении Каза: {e}")
            return {prayer: 0 for prayer in self.PRAYER_CODES.keys()}
    
    def add_qaza(self, user_id: int, prayer: str, count: int = 1) -> bool:
        """Добавить Каза молитвы"""
        try:
            current_qaza = self.get_qaza_count(user_id)
            current_qaza[prayer] += count
            
            # Обновляем в таблице
            values = self.sheet_manager.get_values(self.SHEET_RANGE)
            
            for i, row in enumerate(values):
                if row and int(row[0]) == user_id:
                    # Обновляем существующую строку
                    updated_row = [
                        str(user_id),
                        str(current_qaza["Fajr"]),
                        str(current_qaza["Dhuhr"]),
                        str(current_qaza["Asr"]),
                        str(current_qaza["Maghrib"]),
                        str(current_qaza["Isha"])
                    ]
                    
                    range_name = f"Qaza!A{i+1}:F{i+1}"
                    self.sheet_manager.update_values(range_name, [updated_row])
                    logger.info(f"✅ Добавлено {count} Каза {prayer} для {user_id}")
                    return True
            
            # Если пользователя нет, добавляем новую строку
            new_row = [
                str(user_id),
                str(current_qaza["Fajr"]),
                str(current_qaza["Dhuhr"]),
                str(current_qaza["Asr"]),
                str(current_qaza["Maghrib"]),
                str(current_qaza["Isha"])
            ]
            
            self.sheet_manager.append_values(self.SHEET_RANGE, [new_row])
            logger.info(f"✅ Создана новая запись Каза для {user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при добавлении Каза: {e}")
            return False
    
    def remove_qaza(self, user_id: int, prayer: str, count: int = 1) -> bool:
        """Уменьшить Каза молитвы (отметить выполненную)"""
        try:
            current_qaza = self.get_qaza_count(user_id)
            
            if current_qaza[prayer] < count:
                logger.warning(f"⚠️ Недостаточно Каза молитв {prayer} для {user_id}")
                return False
            
            current_qaza[prayer] -= count
            
            # Обновляем в таблице
            values = self.sheet_manager.get_values(self.SHEET_RANGE)
            
            for i, row in enumerate(values):
                if row and int(row[0]) == user_id:
                    updated_row = [
                        str(user_id),
                        str(current_qaza["Fajr"]),
                        str(current_qaza["Dhuhr"]),
                        str(current_qaza["Asr"]),
                        str(current_qaza["Maghrib"]),
                        str(current_qaza["Isha"])
                    ]
                    
                    range_name = f"Qaza!A{i+1}:F{i+1}"
                    self.sheet_manager.update_values(range_name, [updated_row])
                    logger.info(f"✅ Выполнено {count} Каза {prayer} для {user_id}")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка при уменьшении Каза: {e}")
            return False
    
    def get_total_qaza(self, user_id: int) -> int:
        """Получить общее количество Каза молитв"""
        try:
            qaza = self.get_qaza_count(user_id)
            total = sum(qaza.values())
            logger.info(f"📊 Всего Каза молитв для {user_id}: {total}")
            return total
        except Exception as e:
            logger.error(f"❌ Ошибка при подсчёте общего Каза: {e}")
            return 0
    
    def format_qaza_message(self, user_id: int) -> str:
        """Форматировать сообщение со статусом Каза"""
        try:
            qaza = self.get_qaza_count(user_id)
            total = sum(qaza.values())
            
            if total == 0:
                return "✅ У вас нет пропущенных молитв (Каза)"
            
            message = f"📋 **Ваши пропущенные молитвы (Каза):**\n\n"
            
            for prayer, count in qaza.items():
                if count > 0:
                    emoji = "🌅" if prayer == "Fajr" else "☀️" if prayer == "Dhuhr" else "🌤️" if prayer == "Asr" else "🌅" if prayer == "Maghrib" else "🌙"
                    message += f"{emoji} {time_utils.get_prayer_name_ru(prayer)}: {count}\n"
            
            message += f"\n📊 **Всего:** {total} молитв"
            return message
        except Exception as e:
            logger.error(f"❌ Ошибка при форматировании Каза: {e}")
            return "❌ Ошибка при получении данных Каза"

# ✅ Глобальный экземпляр
qaza_tracker = QazaTracker()
