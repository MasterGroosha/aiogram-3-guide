import asyncio

import structlog
from structlog.typing import FilteringBoundLogger

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from bot.config import Settings
from bot.handlers import get_routers
from bot.logging_config import get_structlog_config

logger: FilteringBoundLogger = structlog.get_logger()


# async def set_bot_commands(bot: Bot) -> None:
#     await bot.set_my_commands([
#         BotCommand(command="sendrich", description="Богатое сообщение"),
#         BotCommand(command="sendrichstream", description="Богатое сообщение со стримингом"),
#         BotCommand(command="sendrichmedia", description="Богатое сообщение с картинками"),
#     ])


async def main() -> None:
    settings = Settings()
    structlog.configure(**get_structlog_config(settings.logs))

    bot = Bot(
        token=settings.bot.token.get_secret_value(),
    )

    dp = Dispatcher()
    dp.include_routers(*get_routers())

    # await set_bot_commands(bot)

    await logger.ainfo("Starting polling...")
    try:
        await dp.start_polling(bot)
    finally:
        await logger.ainfo("Bot stopped")


asyncio.run(main())
