"""
Утилиты для работы с временем молитв
"""
from datetime import datetime
from typing import Dict, List, Optional

# Эмодзи для молитв
PRAYER_EMOJIS = {
    "Fajr": "🌅",
    "Dhuhr": "☀️",
    "Asr": "🌤️",
    "Maghrib": "🌅",
    "Isha": "🌙"
}

class TimeUtils:
    """Класс для работы с временем молитв"""
    
    PRAYER_NAMES_RU = {
        "Fajr": "Фаджр",
        "Dhuhr": "Зухр",
        "Asr": "Аср",
        "Maghrib": "Магриб",
        "Isha": "Иша"
    }
    
    PRAYER_ORDER = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
    
    def get_prayer_name_ru(self, prayer: str) -> str:
        """Возвращает название молитвы на русском"""
        return self.PRAYER_NAMES_RU.get(prayer, prayer)
    
    def is_prayer_passed(self, prayer_time: str, current_time: Optional[str] = None) -> bool:
        """Проверяет прошла ли молитва"""
        try:
            # Парсим время молитвы (формат HH:MM)
            prayer_hour, prayer_minute = map(int, prayer_time.split(":"))
            prayer_dt = datetime.now().replace(hour=prayer_hour, minute=prayer_minute, second=0, microsecond=0)
            
            # Сравниваем с текущим временем
            current_dt = datetime.now()
            
            return current_dt >= prayer_dt
        except Exception as e:
            print(f"❌ Ошибка в is_prayer_passed: {e}")
            return False
    
    def get_passed_prayers(self, prayer_times: Dict[str, str], date_str: Optional[str] = None) -> List[str]:
        """Возвращает список молитв которые уже прошли"""
        passed = []
        
        try:
            for prayer in self.PRAYER_ORDER:
                if prayer not in prayer_times:
                    continue
                
                time_str = prayer_times[prayer]
                
                if self.is_prayer_passed(time_str, date_str):
                    passed.append(prayer)
        except Exception as e:
            print(f"❌ Ошибка в get_passed_prayers: {e}")
        
        return passed
    
    def get_next_prayer(self, prayer_times: Dict[str, str]) -> Optional[str]:
        """Возвращает название следующей молитвы"""
        try:
            for prayer in self.PRAYER_ORDER:
                if prayer not in prayer_times:
                    continue
                
                if not self.is_prayer_passed(prayer_times[prayer]):
                    return prayer
        except Exception as e:
            print(f"❌ Ошибка в get_next_prayer: {e}")
        
        return None

# ✅ Глобальный экземпляр
time_utils = TimeUtils()
