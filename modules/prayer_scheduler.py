from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, time, timedelta
import pytz
from aiogram import Bot
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import config
from logger import logger
from typing import Dict, Optional

class PrayerScheduler:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler(timezone=config.TIMEZONE)
        self.scheduled_jobs = {}
        self.current_prayer_times: Dict[str, str] = {}
        self.user_id = None
    
    def set_user_id(self, user_id: int):
        """Установить ID пользователя"""
        self.user_id = user_id
        logger.info(f"📱 User ID установлен: {user_id}")
    
    async def initialize(self, user_id: int):
        """Инициализировать планировщик"""
        self.set_user_id(user_id)
        logger.info("🚀 Prayer Scheduler инициализирован")
    
    def stop(self):
        """Остановить планировщик"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("🛑 Prayer Scheduler остановлен")

prayer_scheduler: Optional[PrayerScheduler] = None

def init_prayer_scheduler(bot: Bot) -> PrayerScheduler:
    global prayer_scheduler
    prayer_scheduler = PrayerScheduler(bot)
    return prayer_scheduler

