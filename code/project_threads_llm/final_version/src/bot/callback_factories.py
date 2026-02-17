from aiogram.filters.callback_data import CallbackData


class ChoosePromptFactory(CallbackData, prefix="prompt_style"):
    style: str
