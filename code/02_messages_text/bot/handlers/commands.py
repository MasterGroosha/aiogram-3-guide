from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="basic_commands")


@router.message(Command("start"))
async def cmd_start(
        message: Message,
) -> None:
    await message.answer(
        "Привет и добро пожаловать!"
    )
