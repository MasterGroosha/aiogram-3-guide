from aiogram.fsm.state import StatesGroup, State


class SaveCommon(StatesGroup):
    waiting_for_save_start = State()


class DeleteCommon(StatesGroup):
    waiting_for_delete_start = State()


class TextSave(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
