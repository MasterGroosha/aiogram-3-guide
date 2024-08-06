from typing import Union, Dict, Any

from aiogram.filters import BaseFilter
from aiogram.types import Message


class HasLinkFilter(BaseFilter):
    async def __call__(self, message: Message) -> Union[bool, Dict[str, Any]]:
        # Если entities вообще нет, вернётся None,
        # в этом случае считаем, что это пустой список
        entities = message.entities or []

        # Если есть хотя бы одна ссылка, возвращаем её
        for entity in entities:
            if entity.type == "url":
                return {"link": entity.extract_from(message.text)}

        # Если ничего не нашли, возвращаем None
        return False
