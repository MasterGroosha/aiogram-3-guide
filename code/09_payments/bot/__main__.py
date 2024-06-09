import asyncio

import structlog
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from structlog.typing import FilteringBoundLogger

from bot.config_reader import get_config, BotConfig, LogConfig
from bot.fluent_loader import get_fluent_localization
from bot.handlers import get_routers
from bot.logs import get_structlog_config
from bot.middlewares import L10nMiddleware


async def main():
    log_config: LogConfig = get_config(model=LogConfig, root_key="logs")
    structlog.configure(**get_structlog_config(log_config))

    locale = get_fluent_localization()

    dp = Dispatcher()

    # Регистрация мидлвари на типы Message и PreCheckoutQuery
    dp.message.outer_middleware(L10nMiddleware(locale))
    dp.pre_checkout_query.outer_middleware(L10nMiddleware(locale))

    dp.include_routers(*get_routers())

    bot_config: BotConfig = get_config(model=BotConfig, root_key="bot")
    bot = Bot(
        token=bot_config.token.get_secret_value(),
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )

    logger: FilteringBoundLogger = structlog.get_logger()
    await logger.ainfo("Starting polling...")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
