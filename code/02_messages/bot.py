#!venv/bin/python
import logging
from aiogram import Bot, Dispatcher, executor, types
import aiogram.utils.markdown as fmt
from os import getenv
from sys import exit

bot_token = getenv("BOT_TOKEN")
if not bot_token:
    exit("Error: no token provided")

bot = Bot(token=bot_token)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)


@dp.message_handler(commands="test")
async def cmd_test(message: types.Message):
    await message.answer("Hello, <b>world</b>!", parse_mode=types.ParseMode.HTML)
    # Вместо Enum-а можно задать parse_mode в виде обычной строки:
    await message.answer("Hello, *world*\!", parse_mode="MarkdownV2")


@dp.message_handler(commands="test2")
async def cmd_test2(message: types.Message):
    await message.answer("Сообщение с <u>HTML-разметкой</u>")
    await message.answer("Сообщение без <s>какой-либо разметки</s>", parse_mode="")


@dp.message_handler(commands="test3")
async def show_dynamic_formatting(message: types.Message):
    print("OK")
    await message.answer(
        fmt.text(
            fmt.text(fmt.hunderline("Яблоки"), ", вес 1 кг."),
            fmt.text("Старая цена:", fmt.hstrikethrough(50), "рублей"),
            fmt.text("Новая цена:", fmt.hbold(25), "рублей"),
            sep="\n"
        ), parse_mode="HTML"
    )


@dp.message_handler(commands="test4")
async def with_hidden_link(message: types.Message):
    await message.answer(f"{fmt.hide_link('https://telegram.org/blog/video-calls/ru')}Кто бы мог подумать, что "
                         f"в 2020 году в Telegram появятся видеозвонки!\n\nОбычные голосовые вызовы "
                         f"возникли в Telegram лишь в 2017, заметно позже своих конкурентов. А спустя три года, "
                         f"когда огромное количество людей на планете приучились работать из дома из-за эпидемии "
                         f"коронавируса, команда Павла Дурова не растерялась и сделала качественные "
                         f"видеозвонки на WebRTC!\n\nP.S. а ещё ходят слухи про демонстрацию своего экрана :)",
                         parse_mode=types.ParseMode.HTML)


@dp.message_handler(content_types=[types.ContentType.DOCUMENT])
async def download_doc(message: types.Message):
    # Скачивание в каталог с ботом с созданием подкаталогов по типу файла
    await message.document.download()


# Типы содержимого тоже можно указывать по-разному.
@dp.message_handler(content_types=["photo"])
async def download_photo(message: types.Message):
    # Убедитесь, что каталог /tmp/somedir существует!
    await message.photo[-1].download(destination="/tmp/somedir/")


@dp.message_handler(content_types=[types.ContentType.ANIMATION])
async def echo_document(message: types.Message):
    await message.reply_animation(message.animation.file_id)


@dp.message_handler()
async def any_text_message(message: types.Message):
    await message.answer(message.text)
    await message.answer(message.md_text)
    await message.answer(message.html_text)
    await message.answer(f"<u>Ваш текст</u>:\n\n{message.html_text}", parse_mode="HTML")


# Этот хэндлер не будет вызван, если хэндлер функции any_text_message() определён выше!
@dp.message_handler()
async def any_text_message2(message: types.Message):
    await message.answer(f"Привет, <b>{fmt.quote_html(message.text)}</b>", parse_mode=types.ParseMode.HTML)
    # А можно и так:
    await message.answer(fmt.text("Привет,", fmt.hbold(message.text)), parse_mode=types.ParseMode.HTML)


if __name__ == "__main__":
    # Запускаем бота и пропускаем все накопленые входящие
    executor.start_polling(dp, skip_updates=True)
