import re

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message

router = Router(name="deeplinks")


@router.message(Command("help"))
@router.message(CommandStart(
    deep_link=True, magic=F.args == "help"
))
async def cmd_start_help(message: Message) -> None:
    await message.answer("Это сообщение со справкой")


@router.message(CommandStart(
    deep_link=True,
    magic=F.args.regexp(re.compile(r'book_(\d+)'))
))
async def cmd_start_book(
        message: Message,
        command: CommandObject
) -> None:
    book_number = command.args.split("_")[1]
    await message.answer(f"Sending book №{book_number}")
