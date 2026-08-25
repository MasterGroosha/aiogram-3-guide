from aiogram import F, Router
from aiogram.types import Message

router = Router(name="service_messages")


@router.message(F.new_chat_members)
async def somebody_added(message: Message) -> None:
    for user in message.new_chat_members:
        # проперти full_name берёт сразу имя И фамилию
        await message.reply(f"Привет, {user.full_name}")
