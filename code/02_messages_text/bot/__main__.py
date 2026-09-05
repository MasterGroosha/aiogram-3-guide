import asyncio

import structlog
from structlog.typing import FilteringBoundLogger

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from bot.config import Settings
from bot.handlers import get_routers
from bot.logging_config import get_structlog_config

logger: FilteringBoundLogger = structlog.get_logger()


# async def set_bot_commands(bot: Bot) -> None:
#     await bot.set_my_commands([
#         BotCommand(command="test", description="Примеры parse_mode"),
#         BotCommand(command="hello", description="Приветствие с экранированием"),
#         BotCommand(command="advanced_example", description="Продвинутое форматирование"),
#         BotCommand(command="settimer", description="Разбор аргументов команды"),
#         BotCommand(command="links", description="Варианты предпросмотра ссылок"),
#         BotCommand(command="hidden_link", description="Скрытая ссылка в тексте"),
#     ])


async def main() -> None:
    settings = Settings()
    structlog.configure(**get_structlog_config(settings.logs))

    bot = Bot(
        token=settings.bot.token.get_secret_value(),
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        ),
    )

    dp = Dispatcher()
    dp.include_routers(*get_routers())

    # await set_bot_commands(bot)

    await logger.ainfo("Starting polling...")
    try:
        # Запускаем бота и пропускаем все накопленные входящие
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await logger.ainfo("Bot stopped")


asyncio.run(main())
