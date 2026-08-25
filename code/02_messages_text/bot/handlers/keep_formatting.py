from datetime import datetime

from aiogram import F, Router, html
from aiogram.enums import ParseMode
from aiogram.types import Message


router = Router()


@router.message(F.text)
async def echo_with_time(message: Message) -> None:
    # Получаем текущее время в часовом поясе ПК
    time_now = datetime.now().strftime('%H:%M')
    # Создаём подчёркнутый текст
    added_text = html.underline(f"Создано в {time_now}")
    # Отправляем новое сообщение с добавленным текстом
    await message.answer(
        f"{message.html_text}\n\n{added_text}",
        parse_mode=ParseMode.HTML,
    )
