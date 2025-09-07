# Handler for bot status changes in groups
from aiogram import F, Router, Bot                               # Core aiogram components
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, IS_NOT_MEMBER, MEMBER, ADMINISTRATOR  # Chat member status filters
from aiogram.types import ChatMemberUpdated                     # Event types

# Create router for bot status in groups
router = Router()

# Filter to handle only group and supergroup chats
router.my_chat_member.filter(F.chat.type.in_({"group", "supergroup"}))

# Chat type variants for localized messages
chats_variants = {
    "group": "group",
    "supergroup": "supergroup"
}


# Note: Unable to reproduce the case of bot being added as Restricted,
# so there will be no example for that scenario


@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=IS_NOT_MEMBER >> ADMINISTRATOR
    )
)
async def bot_added_as_admin(event: ChatMemberUpdated):
    """
    Handler for when bot is added as administrator
    This is the simplest case - bot can easily send messages
    """
    await event.answer(
        text=f"Hello! Thank you for adding me to "
             f'the {chats_variants[event.chat.type]} "{event.chat.title}" '
             f"as an administrator. Chat ID: {event.chat.id}"
    )


@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=IS_NOT_MEMBER >> MEMBER
    )
)
async def bot_added_as_member(event: ChatMemberUpdated, bot: Bot):
    """
    Handler for when bot is added as regular member
    More complex case: bot might not have permission to send messages,
    so we check permissions first
    """
    # Check if bot has permission to send messages
    chat_info = await bot.get_chat(event.chat.id)
    if chat_info.permissions.can_send_messages:
        await event.answer(
            text=f"Hello! Thank you for adding me to "
                 f'the {chats_variants[event.chat.type]} "{event.chat.title}" '
                 f"as a regular member. Chat ID: {event.chat.id}"
        )
    else:
        # Log this situation somehow (bot can't send messages)
        print("Bot was added but cannot send messages - logging this situation")