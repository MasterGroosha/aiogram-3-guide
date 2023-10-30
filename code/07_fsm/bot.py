import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
# Доп. импорт для раздела про стратегии FSM
from aiogram.fsm.strategy import FSMStrategy

# файл config_reader.py можно взять из репозитория
# пример — в первой главе
from config_reader import config
from handlers import common, ordering_food, ordering_drinks


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # Если не указать storage, то по умолчанию всё равно будет MemoryStorage
    # Но явное лучше неявного =]
    dp = Dispatcher(storage=MemoryStorage())
    # Для выбора другой стратегии FSM:
    # dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.CHAT)
    bot = Bot(config.bot_token.get_secret_value())

    dp.include_routers(common.router, ordering_food.router, ordering_drinks.router)
    # сюда импортируйте ваш собственный роутер для напитков

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
