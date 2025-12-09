"""
Главный файл Prayer Tracker Bot
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import config
from modules.handlers import router
from modules.prayer_scheduler import prayer_scheduler
from data.sheets_manager import sheets_manager
from logger import setup_logger

logger = setup_logger(__name__)

async def set_commands(bot: Bot):
    """Устанавливает команды бота в Telegram"""
    commands = [
        BotCommand(command="start", description="🔄 Главное меню"),
        BotCommand(command="stop", description="⏸️ Остановить уведомления"),
        BotCommand(command="times", description="📅 Времена намазов"),
    ]
    await bot.set_my_commands(commands)
    logger.info("✅ Команды бота установлены")

async def main():
    """Главная функция бота"""
    try:
        logger.info("🚀 Инициализация бота...")
        
        # Инициализируем Bot и Dispatcher
        bot = Bot(token=config.bot_token, parse_mode="Markdown")
        dp = Dispatcher()
        
        # Подключаем роутер обработчиков
        dp.include_router(router)
        logger.info("✅ Роутер обработчиков подключен")
        
        # Инициализируем Google Sheets
        sheets_manager.initialize()
        logger.info("✅ Google Sheets инициализирован")
        
        # Инициализируем планировщик молитв
        prayer_scheduler.set_dispatcher_and_bot(dp, bot)
        logger.info("✅ Планировщик молитв инициализирован")
        
        # Планируем ежедневные молитвы
        await prayer_scheduler.schedule_daily_prayers()
        logger.info("✅ Ежедневные молитвы запланированы")
        
        # Устанавливаем команды
        await set_commands(bot)
        
        logger.info("🎯 Начинаю опрос обновлений (polling)...")
        await dp.start_polling(bot)
        
    except KeyboardInterrupt:
        logger.info("⏹️ Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Ошибка в main: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
