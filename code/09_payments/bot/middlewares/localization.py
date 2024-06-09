from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message
from fluent.runtime import FluentLocalization


# Это будет inner-мидлварь на сообщения
class L10nMiddleware(BaseMiddleware):
    def __init__(
        self,
        locale: FluentLocalization
    ):
        self.locale = locale

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        data["l10n"] = self.locale
        return await handler(event, data)
