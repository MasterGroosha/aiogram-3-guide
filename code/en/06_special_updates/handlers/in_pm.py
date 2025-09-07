# Handler for private messages and user tracking
from aiogram import F, Router                                    # Core aiogram components
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, MEMBER, KICKED                     # Chat member status filters
from aiogram.filters.command import \
    CommandStart, Command                                        # Command filters
from aiogram.types import ChatMemberUpdated, Message            # Event types

# Create router for private message handlers
router = Router()

# Filter to handle only private chats
router.my_chat_member.filter(F.chat.type == "private")
router.message.filter(F.chat.type == "private")

# Example user tracking set
# WARNING: This is for demonstration only!
# In real applications, use more reliable storage like database
users = {111, 222}


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=KICKED)
)
async def user_blocked_bot(event: ChatMemberUpdated):
    """
    Handler for when user blocks the bot
    Removes user from active users set
    """
    users.discard(event.from_user.id)


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=MEMBER)
)
async def user_unblocked_bot(event: ChatMemberUpdated):
    """
    Handler for when user unblocks the bot
    Adds user back to active users set
    """
    users.add(event.from_user.id)


@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    Handler for /start command
    Welcomes user and adds them to users set
    """
    await message.answer("Hello! Welcome to the bot.")
    users.add(message.from_user.id)


@router.message(Command("users"))
async def cmd_users(message: Message):
    """
    Handler for /users command
    Shows list of all tracked users
    """
    if users:
        user_list = "\n".join(f"• {user_id}" for user_id in users)
        await message.answer(f"Active users:\n{user_list}")
    else:
        await message.answer("No active users found.")