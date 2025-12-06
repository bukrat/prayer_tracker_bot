from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from modules.fsm_states import PrayerStates
from modules.prayer_scheduler import prayer_scheduler
from logger import logger

router = Router()

@router.message(Command('start'))
async def start_handler(message: Message, state: FSMContext):
    """Стартовое сообщение"""
    await state.clear()
    
    # Инициализируем планировщик
    if prayer_scheduler:
        await prayer_scheduler.initialize(message.from_user.id)
    
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
    if not prayer_scheduler or not prayer_scheduler.current_prayer_times:
        await message.answer("❌ Времена не загружены. Напиши /start")
        return
    
    times_text = "📅 **Времена намаза на сегодня:**\n\n"
    for prayer, time_str in prayer_scheduler.current_prayer_times.items():
        emoji = prayer_scheduler._get_prayer_emoji(prayer)
        times_text += f"{emoji} {prayer}: {time_str}\n"
    
    await message.answer(times_text, parse_mode="Markdown")

@router.message(F.text.contains("Читал"))
async def prayer_yes_handler(message: Message):
    """Пользователь прочитал"""
    if prayer_scheduler:
        await prayer_scheduler.handle_prayer_response(message.text)
    
    await message.answer("✅ Хорошо! Спасибо за ответ.")
    logger.info(f"User {message.from_user.id} прочитал намаз")

@router.message(F.text.contains("Не читал"))
async def prayer_no_handler(message: Message):
    """Пользователь не прочитал"""
    if prayer_scheduler:
        await prayer_scheduler.handle_prayer_response(message.text)
    
    await message.answer("😔 Постарайся в следующий раз!")
    logger.info(f"User {message.from_user.id} не прочитал намаз")

@router.message(Command('stop'))
async def stop_handler(message: Message):
    """Остановить трекинг"""
    if prayer_scheduler:
        prayer_scheduler.stop()
    await message.answer("🛑 Трекинг остановлен")

