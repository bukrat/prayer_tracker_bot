"""
Планировщик молитв - отправляет напоминания о молитвах
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot, Dispatcher
from datetime import datetime
import logging

from config import config
from logger import setup_logger

logger = setup_logger(__name__)

# Список напоминаний для мотивации
PRAYER_REMINDERS = [
    "Помолись и почувствуй мир в своём сердце",
    "Намаз - это связь между тобой и Аллахом",
    "Молитва дарует спокойствие и силу",
    "Аллах близок к тем, кто молится",
    "Регулярная молитва - путь к успеху",
]

class PrayerScheduler:
    """Класс для планирования напоминаний о молитвах"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.user_ids = set()
        self.bot = None
        self.dispatcher = None
    
    def set_dispatcher_and_bot(self, dispatcher: Dispatcher, bot: Bot):
        """Устанавливает диспетчер и бота"""
        self.dispatcher = dispatcher
        self.bot = bot
        logger.info("✅ Dispatcher и Bot установлены в scheduler")
    
    async def initialize(self):
        """Инициализирует планировщик"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("✅ Планировщик инициализирован")
    
    async def schedule_daily_prayers(self):
        """Планирует ежедневные напоминания о молитвах"""
        try:
            await self.initialize()
            logger.info("✅ Ежедневные молитвы запланированы")
        except Exception as e:
            logger.error(f"❌ Ошибка при планировании молитв: {e}", exc_info=True)
    
    async def send_prayer_reminder(self, prayer_name: str, prayer_ru: str, emoji: str):
        """Отправляет напоминание о молитве пользователям"""
        try:
            if not self.bot:
                logger.warning("❌ Bot не инициализирован")
                return
            
            logger.info(f"📢 Отправляю напоминание о {prayer_ru}")
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке напоминания: {e}", exc_info=True)

# ✅ Глобальный экземпляр планировщика
prayer_scheduler = PrayerScheduler()
