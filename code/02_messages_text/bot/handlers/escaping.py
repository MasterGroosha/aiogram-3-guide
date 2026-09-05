from aiogram import Router, html
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.formatting import Text, Bold

router = Router(name="escaping")


@router.message(Command("hello"))
async def cmd_hello(message: Message):
    await message.answer(
        # специальный атрибут full_name собирает
        # first_name и last_name (при наличии) за вас
        f"Hello, {html.bold(html.quote(message.from_user.full_name))}",
        parse_mode=ParseMode.HTML
    )


@router.message(Command("hello2"))
async def cmd_hello2(message: Message):
    content = Text(
        "Hello, ",
        Bold(message.from_user.full_name)
    )
    await message.answer(
        **content.as_kwargs()
    )