from aiogram.fsm.state import StatesGroup, State


class NewChatFlow(StatesGroup):
    choosing_persona = State()