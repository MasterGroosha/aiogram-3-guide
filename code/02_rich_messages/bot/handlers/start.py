from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(
        message: Message,
) -> None:
    await message.answer(
        "Привет! Вот что умеет этот бот:\n\n"
        "/sendrich — отправить Rich HTML-сообщение с таблицей и формулой\n"
        "/sendrichstream — показать стриминг черновика Rich-сообщения\n"
        "/sendrichmedia — отправить галерею HTTP-котиков\n\n"
        "Также можно переслать боту любой rich message — он его разберёт по кусочкам."
    )
