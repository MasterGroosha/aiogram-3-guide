from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="formatting")


# Если не указать фильтр F.text,
# то хэндлер сработает даже на картинку с подписью /test
@router.message(F.text, Command("test"))
async def any_message(message: Message) -> None:
    await message.answer(
        "Hello, <b>world</b>!",
        parse_mode=ParseMode.HTML
    )
    await message.answer(
        "Hello, *world*\!",
        parse_mode=ParseMode.MARKDOWN_V2
    )
    await message.answer("Сообщение с <u>HTML-разметкой</u>")
    # чтобы явно отключить форматирование в конкретном запросе,
    # передайте parse_mode=None
    await message.answer(
        "Сообщение без <s>какой-либо разметки</s>",
        parse_mode=None
    )
