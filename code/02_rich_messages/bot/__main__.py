import asyncio

import structlog
from structlog.typing import FilteringBoundLogger

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from bot.config import Settings
from bot.handlers import get_routers
from bot.logging_config import get_structlog_config

logger: FilteringBoundLogger = structlog.get_logger()


async def set_bot_commands(bot: Bot) -> None:
    await bot.set_my_commands([
        BotCommand(command="sendrich", description="Богатое сообщение"),
        BotCommand(command="sendrichblocks", description="Богатое сообщение из блоков"),
        BotCommand(command="sendrichbuttons", description="Богатое сообщение с кнопками внутри"),
        BotCommand(command="sendrichedit", description="Богатое сообщение с редактированием"),
        BotCommand(command="sendricheditblocks", description="Чек-лист на блоках"),
        BotCommand(command="sendrichstream", description="Богатое сообщение со стримингом"),
        BotCommand(command="sendrichstreamstop", description="Стриминг с кнопкой остановки"),
        BotCommand(command="sendrichmedia", description="Богатое сообщение с картинками"),
        BotCommand(command="sendrichmediafile", description="Картинка с диска внутри сообщения"),
        BotCommand(command="sendrichmediafileid", description="Картинка по file_id внутри сообщения"),
        BotCommand(command="sendrichdoc", description="Документ внутри сообщения"),
    ])


async def main() -> None:
    settings = Settings()
    structlog.configure(**get_structlog_config(settings.logs))

    bot = Bot(
        token=settings.bot.token.get_secret_value(),
    )

    dp = Dispatcher()
    dp.include_routers(*get_routers())

    await set_bot_commands(bot)

    await logger.ainfo("Starting polling...")
    try:
        await dp.start_polling(bot)
    finally:
        await logger.ainfo("Bot stopped")


asyncio.run(main())
