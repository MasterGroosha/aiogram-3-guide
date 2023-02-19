from aiogram import F
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()
router.message.filter(F.chat.type.in_({"group", "supergroup"}))


@router.message(Command("dice"))
async def cmd_dice_in_group(message: Message):
    await message.answer_dice(emoji="🎲")


@router.message(Command("basketball"))
async def cmd_basketball_in_group(message: Message):
    await message.answer_dice(emoji="🏀")
