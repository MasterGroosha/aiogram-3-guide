import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.dispatcher.fsm.storage.memory import MemoryStorage

# файл config_reader.py можно взять из репозитория
# пример — в первой главе
from config_reader import config
from handlers import common, ordering_food


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # Если не указать storage, то по умолчанию всё равно будет MemoryStorage
    # Но явное лучше неявного =]
    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(config.bot_token.get_secret_value())

    dp.include_router(common.router)
    dp.include_router(ordering_food.router)
    # сюда импортируйте ваш собственный роутер для напитков

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    asyncio.run(main())
