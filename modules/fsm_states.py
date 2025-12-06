from aiogram.fsm.state import State, StatesGroup

class PrayerStates(StatesGroup):
    waiting_prayer_confirmation = State()

