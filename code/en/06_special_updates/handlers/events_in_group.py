# Handler for group events and admin commands
from aiogram import Router, F                                   # Core aiogram components
from aiogram.filters.command import Command                     # Command filters
from aiogram.types import Message                               # Message types

# Create router for group events
router = Router()

# Note: You could actually apply a custom filter to the router
# to check if the caller's ID is in the admins set.
# Then all handlers in the router would automatically be called
# only for people from admins, reducing code and eliminating unnecessary if statements.
# But for demonstration purposes, we'll use if-else to make it clearer.


@router.message(Command("ban"), F.reply_to_message)
async def cmd_ban(message: Message, admins: set[int]):
    """
    Handler for /ban command
    Allows administrators to ban users by replying to their message
    """
    # Check if the user has admin rights
    if message.from_user.id not in admins:
        await message.answer("You don't have sufficient permissions to perform this action")
    else:
        # Ban the user who was replied to
        await message.chat.ban(
            user_id=message.reply_to_message.from_user.id
        )
        await message.answer("Violator has been banned")