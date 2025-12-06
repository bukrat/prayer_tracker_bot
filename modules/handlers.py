from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from modules.fsm_states import PrayerStates
from logger import logger

router = Router()

@router.message(Command('start'))
async def start_handler(message: Message, state: FSMContext):
    """Стартовое сообщение"""
    await state.clear()
    
    await message.answer(
        "🕌 **Добро пожаловать в Prayer Tracker!**\n\n"
        "Я буду напоминать тебе о времени намаза и спрашивать, "
        "прочитал ли ты после каждого намаза.\n\n"
        "Команды:\n"
        "/times - Сегодняшние времена намаза\n"
        "/stop - Остановить трекинг",
        parse_mode="Markdown"
    )

@router.message(Command('times'))
async def times_handler(message: Message):
    """Показать времена намаза на сегодня"""
    await message.answer("📅 Функция находится в разработке")

@router.message(F.text.contains("Да"))
async def prayer_yes_handler(message: Message):
    """Пользователь ответил Да"""
    await message.answer("✅ Хорошо! Спасибо за ответ.")

@router.message(F.text.contains("Нет"))
async def prayer_no_handler(message: Message):
    """Пользователь ответил Нет"""
    await message.answer("😔 Постарайся в следующий раз!")

@router.message(Command('stop'))
async def stop_handler(message: Message):
    """Остановить трекинг"""
    await message.answer("🛑 Трекинг остановлен")

