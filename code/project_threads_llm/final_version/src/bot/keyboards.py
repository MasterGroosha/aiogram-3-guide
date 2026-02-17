from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callback_factories import ChoosePromptFactory
from bot.prompts import prompts, available_personas
from bot.text_utils import smart_capitalize


def make_prompt_keyboard():
    builder = InlineKeyboardBuilder()
    for persona in available_personas():
        builder.button(
            text=smart_capitalize(prompts[persona]["name"]),
            callback_data=ChoosePromptFactory(style=persona),
        )
    builder.adjust(1)
    return builder.as_markup()
