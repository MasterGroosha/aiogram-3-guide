from typing import Union

from aiogram.dispatcher.filters import BaseFilter
from aiogram.types import Message


class ChatTypeFilter(BaseFilter):
    chat_type: Union[str, list]

    async def __call__(self, message: Message) -> bool:
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type
