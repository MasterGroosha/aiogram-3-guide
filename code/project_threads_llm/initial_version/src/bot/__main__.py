import asyncio

import httpx
import structlog
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from aiogram.fsm.strategy import FSMStrategy
from structlog.typing import FilteringBoundLogger

from .config_reader import Settings
from .handlers import get_routers
from .logs import get_structlog_config

logger: FilteringBoundLogger = structlog.get_logger()



async def main():
    settings = Settings()
    structlog.configure(**get_structlog_config(settings.logs))
    bot = Bot(token=settings.bot.token.get_secret_value())

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(*get_routers())

    await logger.ainfo("Starting bot...")
    await dp.start_polling(bot, )


if __name__ == "__main__":
    asyncio.run(main())
