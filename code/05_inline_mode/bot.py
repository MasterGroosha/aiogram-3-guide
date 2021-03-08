import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand

from app.config_reader import load_config
from app.handlers.common_commands import register_handlers_common
from app.handlers.inline_mode import register_inline_handlers
from app.handlers.adding_links import register_add_links_handlers
from app.handlers.manage_links import register_manage_links_handlers

logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/add", description="Добавить новую ссылку"),
        BotCommand(command="/links", description="Просмотр списка ссылок"),
        BotCommand(command="/cancel", description="Отменить текущее действие")
    ]
    await bot.set_my_commands(commands)


async def main():
    # Настройка логирования в stdout
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")

    # Парсинг файла конфигурации
    config = load_config("config/bot.ini")

    # Объявление и инициализация объектов бота и диспетчера
    bot = Bot(token=config.tg_bot.token)
    print((await bot.get_me()).username)
    # В реальных условиях вместо MemoryStorage лучше взять что-то другое
    dp = Dispatcher(bot, storage=MemoryStorage())

    # Регистрация хэндлеров
    register_add_links_handlers(dp)
    register_manage_links_handlers(dp)
    register_handlers_common(dp)
    register_inline_handlers(dp)

    # Установка команд бота
    await set_commands(bot)

    # Запуск поллинга
    # await dp.skip_updates()  # пропуск накопившихся апдейтов (необязательно)
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
