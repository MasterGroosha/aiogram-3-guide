# Этот файл является самодостаточным ботом и может быть запущен отдельно.
import asyncio
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.types import Message

dp = Dispatcher()


@dp.message()
async def any_message(
        message: Message,
):
    await message.answer("Hello world!")


async def main():
    token = getenv("BOT_TOKEN")
    if not token:
        error = "No token provided"
        raise ValueError(error)
    bot = Bot(token=token)

    print("Starting bot...")
    try:
        await dp.start_polling(bot)
    finally:
        print("Bot stopped")


if __name__ == '__main__':
    asyncio.run(main())
