from typing import Union, Dict, Any

from aiogram import Bot
from aiogram.filters import BaseFilter
from aiogram.types import Message


class ViaBotFilter(BaseFilter):
    async def __call__(self, message: Message, bot: Bot) -> Union[bool, Dict[str, Any]]:
        return message.via_bot and message.via_bot.id == bot.id
