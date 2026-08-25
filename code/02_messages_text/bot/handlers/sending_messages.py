from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="basic_commands")


@router.message(Command("answer_and_reply"))
async def cmd_answer_and_reply(
        message: Message,
        bot: Bot,
) -> None:
    await message.answer(
        "Отправка сообщения в тот же чат"
    )
    await message.reply(
        "Отправка сообщения в тот же чат "
        "как ответ на команду"
    )
    await bot.send_message(
        chat_id=-1001234567890,
        text="А это сообщение отправлено в другую группу"
    )
