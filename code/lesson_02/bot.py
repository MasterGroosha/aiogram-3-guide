#!venv/bin/python
import logging
from aiogram import Bot, Dispatcher, executor, types
import aiogram.utils.markdown as md
from os import getenv
from sys import exit

bot_token = getenv("BOT_TOKEN")
if not bot_token:
    exit("Error: no token provided")

bot = Bot(token=bot_token)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

pic_file_id = "some_file_id"


@dp.message_handler(commands="test")
async def cmd_test(message: types.Message):
    await message.answer("Hello, <b>world</b>!", parse_mode=types.ParseMode.HTML)
    # Вместо Enum-а можно задать parse_mode в виде обычной строки:
    await message.answer("Hello, *world*\!", parse_mode="MarkdownV2")


@dp.message_handler(commands="test2")
async def cmd_test2(message: types.Message):
    await message.answer("Сообщение с <u>HTML-разметкой</u>")
    await message.answer("Сообщение без <s>какой-либо разметки</s>", parse_mode="")


@dp.message_handler()
async def any_text_message(message: types.Message):
    await message.answer(message.text)
    await message.answer(message.md_text)
    await message.answer(message.html_text)
    await message.answer(f"<u>Ваш текст</u>:\n\n{message.html_text}", parse_mode="HTML")


@dp.message_handler(commands="bad")
async def renameme(message: types.Message):
    await message.answer(f"Hello, {md.quote_html(message.from_user.first_name)}")
    await message.answer(f"Hello, {md.quote_html(message.from_user.last_name)}")
    await message.answer(f"Hello, {md.quote_html(message.from_user.full_name)}")


@dp.message_handler(commands="bad_md")
async def renameme(message: types.Message):
    await message.answer(f"Hello, {md.escape_md(message.from_user.first_name)}")
    await message.answer(f"Hello, {md.escape_md(message.from_user.last_name)}")
    await message.answer(f"Hello, {md.escape_md(message.from_user.full_name)}")


@dp.message_handler(commands="parse")
async def with_parse(message: types.Message):
    # await message.answer("Hello, <b>Stranger</b>")
    await message.reply_photo(pic_file_id, caption="Hello, <b>Stranger</b>")


@dp.message_handler(commands="noparse")
async def with_noparse(message: types.Message):
    # await message.answer("Hello, <b>Stranger</b>", parse_mode="")
    await message.reply_photo(pic_file_id, caption="Hello, <b>Stranger</b>", parse_mode="")


@dp.message_handler(content_types=types.ContentType.PHOTO)
async def get_photo_id(message: types.Message):
    await message.reply(message.photo[-1].file_id)


if __name__ == "__main__":
    # Запускаем бота и пропускаем все накопленые входящие
    executor.start_polling(dp, skip_updates=True)
