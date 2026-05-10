import asyncio

import structlog
from openai import AsyncOpenAI
from structlog.typing import FilteringBoundLogger

from aiogram import Bot, Dispatcher
from bot.config import Settings
from bot.handlers import get_routers
from bot.logging_config import get_structlog_config

logger: FilteringBoundLogger = structlog.get_logger()

async def main() -> None:
    settings = Settings()
    structlog.configure(**get_structlog_config(settings.logs))

    bot = Bot(
        token=settings.bot.token.get_secret_value(),
    )
    openrouter_client = AsyncOpenAI(
        base_url=settings.llm.base_url,
        api_key=settings.llm.api_key.get_secret_value(),
    )

    with open("bot/system_prompt.txt", "r", encoding="utf-8") as f:
        system_prompt: str = f.read()

    dp = Dispatcher(
        llm_client=openrouter_client,
        llm_model=settings.llm.model_name,
        system_prompt=system_prompt,
    )
    dp.include_routers(*get_routers())

    await logger.ainfo("Starting polling...")
    try:
        await dp.start_polling(bot)
    finally:
        await logger.ainfo("Bot stopped")


asyncio.run(main())
