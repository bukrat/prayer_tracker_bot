from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import pytz
from aiogram import Bot
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import config
from data.sheets_manager import sheets_manager
from logger import logger
from typing import Dict, Optional

class PrayerScheduler:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler(timezone=config.TIMEZONE)
        self.scheduled_jobs = {}
        self.current_prayer_times: Dict[str, str] = {}
        self.user_id = None
        self.last_prayer = None
    
    def set_user_id(self, user_id: int):
        """Установить ID пользователя"""
        self.user_id = user_id
        logger.info(f"📱 User ID установлен: {user_id}")
    
    async def initialize(self, user_id: int):
        """Инициализировать планировщик"""
        self.set_user_id(user_id)
        
        # Загрузить времена намаза на сегодня
        await self.load_today_prayer_times()
        
        # Расписать задачи на сегодня
        await self.schedule_today_prayers()
        
        # Загружать новые времена каждый день в 00:01
        self.scheduler.add_job(
            self.daily_reload,
            CronTrigger(hour=0, minute=1, timezone=config.TIMEZONE),
            id="daily_reload",
            replace_existing=True
        )
        
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("🚀 Prayer Scheduler запущен")
    
    async def load_today_prayer_times(self):
        """Загрузить времена намаза на сегодня из Sheets"""
        self.current_prayer_times = await sheets_manager.get_today_prayer_times()
        
        if not self.current_prayer_times:
            logger.warning("⚠️ Нет времен намаза на сегодня")
            return False
        
        logger.info(f"📅 Времена загружены: {self.current_prayer_times}")
        return True
    
    async def schedule_today_prayers(self):
        """Распланировать уведомления на сегодня"""
        if not self.current_prayer_times:
            logger.warning("❌ Невозможно планировать - нет времен")
            return
        
        tz = pytz.timezone(config.TIMEZONE)
        now = datetime.now(tz)
        
        for prayer_name, prayer_time_str in self.current_prayer_times.items():
            try:
                # Парсим время (формат "HH:MM")
                prayer_hour, prayer_minute = map(int, prayer_time_str.split(":"))
                prayer_datetime = now.replace(
                    hour=prayer_hour,
                    minute=prayer_minute,
                    second=0,
                    microsecond=0
                )
                
                # Если время уже прошло сегодня, пропускаем
                if prayer_datetime < now:
                    logger.info(f"⏭️ {prayer_name} уже прошел в {prayer_time_str}")
                    continue
                
                # Удаляем старую задачу если есть
                job_id = f"prayer_{prayer_name.lower()}"
                try:
                    self.scheduler.remove_job(job_id)
                except:
                    pass
                
                # Добавляем новую задачу
                self.scheduler.add_job(
                    self.send_prayer_notification,
                    trigger='date',
                    run_date=prayer_datetime,
                    args=(prayer_name,),
                    id=job_id,
                    replace_existing=True
                )
                
                logger.info(f"📌 {prayer_name} запланирован на {prayer_time_str}")
                self.scheduled_jobs[prayer_name] = job_id
                
            except Exception as e:
                logger.error(f"❌ Ошибка планирования {prayer_name}: {e}")
    
    async def send_prayer_notification(self, prayer_name: str):
        """Отправить уведомление о намазе"""
        if not self.user_id:
            logger.warning("⚠️ User ID не установлен")
            return
        
        try:
            self.last_prayer = prayer_name
            
            # Отправляем уведомление
            kb = ReplyKeyboardMarkup(
                keyboard=[[
                    KeyboardButton(text="✅ Читал"),
                    KeyboardButton(text="❌ Не читал")
                ]],
                resize_keyboard=True
            )
            
            prayer_time = self.current_prayer_times.get(prayer_name, "??:??")
            prayer_emoji = self._get_prayer_emoji(prayer_name)
            
            await self.bot.send_message(
                chat_id=self.user_id,
                text=f"{prayer_emoji} **Время намаза {prayer_name}!**\n\n"
                     f"⏰ {prayer_time}\n\n"
                     f"_Напоминание придет через 30 минут_",
                parse_mode="Markdown",
                reply_markup=kb
            )
            
            logger.info(f"📬 {prayer_name} уведомление отправлено")
            
            # Логируем отправку в Sheets
            await sheets_manager.log_prayer_notification(prayer_name)
            
            # Планируем напоминание через 30 минут
            reminder_time = datetime.now() + timedelta(minutes=30)
            reminder_job_id = f"reminder_{prayer_name.lower()}"
            
            try:
                self.scheduler.remove_job(reminder_job_id)
            except:
                pass
            
            self.scheduler.add_job(
                self.send_prayer_reminder,
                trigger='date',
                run_date=reminder_time,
                args=(prayer_name,),
                id=reminder_job_id,
                replace_existing=True
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки {prayer_name}: {e}")
    
    async def send_prayer_reminder(self, prayer_name: str):
        """Напоминание через 30 минут"""
        if not self.user_id:
            return
        
        try:
            kb = ReplyKeyboardMarkup(
                keyboard=[[
                    KeyboardButton(text="✅ Читал"),
                    KeyboardButton(text="❌ Не читал")
                ]],
                resize_keyboard=True
            )
            
            await self.bot.send_message(
                chat_id=self.user_id,
                text=f"❓ **Ты уже прочитал {prayer_name}?**",
                parse_mode="Markdown",
                reply_markup=kb
            )
            
            logger.info(f"🔔 Напоминание {prayer_name} отправлено")
            
        except Exception as e:
            logger.error(f"❌ Ошибка напоминания: {e}")
    
    async def handle_prayer_response(self, response: str):
        """Обработать ответ пользователя"""
        if not self.last_prayer:
            return
        
        read_status = "✅ Читал" if "Читал" in response else "❌ Не читал"
        await sheets_manager.update_prayer_response(self.last_prayer, read_status)
        
        logger.info(f"📊 {self.last_prayer}: {read_status}")
    
    async def daily_reload(self):
        """Ежедневная перезагрузка времен (запускается в 00:01)"""
        logger.info("🔄 Ежедневная перезагрузка времен намаза...")
        
        # Очищаем старые задачи
        for prayer_name in list(self.scheduled_jobs.keys()):
            job_id = self.scheduled_jobs[prayer_name]
            try:
                self.scheduler.remove_job(job_id)
            except:
                pass
        
        self.scheduled_jobs.clear()
        
        # Загружаем новые времена и расписываем
        await self.load_today_prayer_times()
        await self.schedule_today_prayers()
        
        logger.info("✅ Перезагрузка завершена")
    
    def _get_prayer_emoji(self, prayer_name: str) -> str:
        """Получить эмодзи для намаза"""
        emojis = {
            "Fajr": "🌅",
            "Dhuhr": "☀️",
            "Asr": "🌤️",
            "Maghrib": "🌆",
            "Isha": "🌙"
        }
        return emojis.get(prayer_name, "🕌")
    
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

