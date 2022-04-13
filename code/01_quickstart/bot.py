import asyncio
import logging

from aiogram import Bot, Dispatcher, types

logging.basicConfig(level=logging.INFO)
bot = Bot(token="TOKEN")
dp = Dispatcher()


# Хэндлер на команду /start
@dp.message(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer("Hello!")


# Хэндлер на команду /test1
@dp.message(commands=["test1"])
async def cmd_test1(message: types.Message):
    await message.answer("Test 1")


# Хэндлер на команду /test2
# Без декоратора, т.к. регистрируется ниже в функции main()
async def cmd_test2(message: types.Message):
    await message.reply("Test 2")


@dp.message(commands=["answer"])
async def cmd_answer(message: types.Message):
    await message.answer("Это простой ответ")


@dp.message(commands=["reply"])
async def cmd_reply(message: types.Message):
    await message.reply('Это ответ с "ответом"')


@dp.message(commands=["dice"])
async def cmd_dice(message: types.Message):
    await message.answer_dice(emoji="🎲")


async def main():
    # Регистрируем хэндлер cmd_test2 по команде /start
    dp.message.register(cmd_test2, commands=["test2"])

    # Запускаем бота и пропускаем все накопленные входящие
    # Да, этот метод можно вызвать даже если у вас поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
