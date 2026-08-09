from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="commands_prefixes")


@router.message(Command("custom1", prefix="%"))
async def cmd_custom1(message: Message) -> None:
    await message.answer("Вижу команду!")


# Можно указать несколько префиксов........vv...
@router.message(Command("custom2", prefix="/!"))
async def cmd_custom2(message: Message) -> None:
    await message.answer("И эту тоже вижу!")
