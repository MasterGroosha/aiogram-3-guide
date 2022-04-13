from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message(content_types="text")
async def message_with_text(message: Message):
    await message.answer("Это текстовое сообщение!")


@router.message(content_types="sticker")
async def message_with_sticker(message: Message):
    await message.answer("Это стикер!")


@router.message(content_types="animation")
async def message_with_gif(message: Message):
    await message.answer("Это GIF!")
