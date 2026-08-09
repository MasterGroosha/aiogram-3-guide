import re

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message

router = Router(name="deeplinks")


@router.message(Command("help"))
@router.message(CommandStart(
    deep_link=True, magic=F.args == "help"
))
async def cmd_help(message: Message):
    await message.answer(
        "Это сообщение показывается как на команду /help, "
        "так и по диплинку t.me/bot?start=help"
    )


@router.message(CommandStart(
    deep_link=True,
    magic=F.args.regexp(re.compile(r"secretfile_(?P<file_id>\d{1,6})"))
))
async def start_secret_file_deeplink(
        message: Message,
        command: CommandObject
):
    file_id = command.magic_result["file_id"]
    await message.answer(f"Отправляю секретный документ №{file_id}")
