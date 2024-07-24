from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message


class ChatTypeFilter(BaseFilter):
    def __init__(self, is_private: bool):
        self.is_private = is_private

    async def __call__(self, message: Message) -> bool:
        return self.is_private == (message.chat.type == 'private')
