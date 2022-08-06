from aiogram import Router, Bot
from aiogram.dispatcher.filters.command import Command
from aiogram.types import Message

router = Router()

# Вообще говоря, можно на роутер навесить кастомный фильтр
# с проверкой, лежит ли айди вызывающего во множестве admins.
# Тогда все хэндлеры в роутере автоматически будут вызываться
# только для людей из admins, это сократит код и избавит от лишнего if
# Но для примера сделаем через if-else, чтобы было нагляднее


@router.message(Command(commands=["ban"]))
async def cmd_ban(message: Message, admins: set[int], bot: Bot):
    if message.from_user.id not in admins:
        await message.answer("У вас недостаточно прав для совершения этого действия")
    else:
        await bot.ban_chat_member(
            chat_id=message.chat.id,
            user_id=message.reply_to_message.from_user.id
        )
        await message.answer("Нарушитель заблокирован")
