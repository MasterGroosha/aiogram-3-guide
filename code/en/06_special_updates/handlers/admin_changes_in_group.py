# Handler for admin status changes in group
from aiogram import F, Router                                    # Core aiogram components
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, KICKED, LEFT, \
    RESTRICTED, MEMBER, ADMINISTRATOR, CREATOR                   # Chat member status filters
from aiogram.types import ChatMemberUpdated                     # Event types

from config_reader import config                                # Configuration

# Create router for admin changes
router = Router()

# Filter to handle only the main chat specified in config
router.chat_member.filter(F.chat.id == config.main_chat_id)


@router.chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=
        (KICKED | LEFT | RESTRICTED | MEMBER)
        >>
        (ADMINISTRATOR | CREATOR)
    )
)
async def admin_promoted(event: ChatMemberUpdated, admins: set[int]):
    """
    Handler for when user is promoted to administrator
    Updates the admins set and notifies about the promotion
    """
    # Add new admin to the tracking set
    admins.add(event.new_chat_member.user.id)
    
    await event.answer(
        f"{event.new_chat_member.user.first_name} "
        f"has been promoted to Administrator!"
    )


@router.chat_member(
    ChatMemberUpdatedFilter(
        # Note the direction of arrows
        # Or we could swap the objects in parentheses
        member_status_changed=
        (KICKED | LEFT | RESTRICTED | MEMBER)
        <<
        (ADMINISTRATOR | CREATOR)
    )
)
async def admin_demoted(event: ChatMemberUpdated, admins: set[int]):
    """
    Handler for when administrator is demoted to regular user
    Removes admin from tracking set and notifies about the demotion
    """
    # Remove admin from the tracking set
    admins.discard(event.new_chat_member.user.id)
    
    await event.answer(
        f"{event.new_chat_member.user.first_name} "
        f"has been demoted to regular user!"
    )