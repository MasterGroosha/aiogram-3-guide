# Import aiogram components
from aiogram import Router, F      # Router for organizing handlers, F for magic filters  
from aiogram.types import Message  # Message type for handling text messages

# Create router instance for this module
# This router handles different types of media content
router = Router()


@router.message(F.text)
async def message_with_text(message: Message):
    """
    Handler for text messages
    Responds when user sends any text message
    """
    await message.answer("This is a text message!")


@router.message(F.sticker)
async def message_with_sticker(message: Message):
    """
    Handler for sticker messages
    Responds when user sends a sticker
    """
    await message.answer("This is a sticker!")


@router.message(F.animation)
async def message_with_gif(message: Message):
    """
    Handler for GIF/animation messages
    Responds when user sends an animated image (GIF)
    """
    await message.answer("This is a GIF!")
