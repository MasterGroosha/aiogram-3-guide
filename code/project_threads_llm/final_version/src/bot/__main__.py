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
from .llm import LLMClient


logger: FilteringBoundLogger = structlog.get_logger()


async def shutdown(dispatcher: Dispatcher) -> None:
    await dispatcher["http_client"].aclose()


async def main():
    settings = Settings()
    structlog.configure(**get_structlog_config(settings.logs))

    bot = Bot(token=settings.bot.token.get_secret_value())

    dp = Dispatcher(
        storage=MemoryStorage(),
        # events_isolation=SimpleEventIsolation(),
        fsm_strategy=FSMStrategy.USER_IN_TOPIC,
    )

    dp.include_routers(*get_routers())
    dp.shutdown.register(shutdown)

    http_client = httpx.AsyncClient(timeout=None)

    llm_client = LLMClient(http_client, settings.llm.url)
    dp.workflow_data.update(
        http_client=http_client,
        llm_client=llm_client,
    )

    await logger.ainfo("Starting bot...")
    await dp.start_polling(bot)


asyncio.run(main())
