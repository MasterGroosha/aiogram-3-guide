# Import aiogram components
from aiogram import Router, F                           # Router for organizing handlers, F for magic filters
from aiogram.filters import Command                     # Filter for handling commands
from aiogram.types import Message, ReplyKeyboardRemove  # Message type and keyboard removal

# Import custom keyboard
from keyboards.for_questions import get_yes_no_kb

# Create router instance for this module
# Router allows organizing handlers into logical groups
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """
    Handler for /start command
    Shows a question with Yes/No keyboard to the user
    """
    await message.answer(
        "Are you satisfied with your job?",
        reply_markup=get_yes_no_kb()
    )


@router.message(F.text.lower() == "yes")
async def answer_yes(message: Message):
    """
    Handler for "Yes" button response
    Responds positively and removes the keyboard
    """
    await message.answer(
        "That's great!",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(F.text.lower() == "no")
async def answer_no(message: Message):
    """
    Handler for "No" button response  
    Responds with sympathy and removes the keyboard
    """
    await message.answer(
        "That's a pity...",
        reply_markup=ReplyKeyboardRemove()
    )
