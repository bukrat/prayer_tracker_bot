import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import config
from logger import logger
from modules.prayer_scheduler import init_prayer_scheduler
from modules.handlers import router

async def set_commands(bot: Bot):
    """Установить команды бота"""
    commands = [
        BotCommand(command="start", description="Начать трекинг"),
        BotCommand(command="times", description="Времена намаза на сегодня"),
        BotCommand(command="stop", description="Остановить трекинг"),
    ]
    await bot.set_my_commands(commands)

async def main():
    """Главная функция"""
    logger.info("🚀 Запуск Prayer Tracker Bot...")
    
    # Инициализация
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    
    # Регистрируем роутер
    dp.include_router(router)
    
    # Инициализируем prayer scheduler
    prayer_scheduler = init_prayer_scheduler(bot)
    
    # Установить команды
    await set_commands(bot)
    
    try:
        logger.info("🎯 Бот запущен!")
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())

