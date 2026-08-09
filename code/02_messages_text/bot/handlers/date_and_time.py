from datetime import datetime

from aiogram import F, Router
from aiogram.types import Message

router = Router(name="date_and_time")


@router.message(F.text == "Дата")
@router.message(F.text == "дата")
async def current_date(
        message: Message,
) -> None:
    await message.answer(f"У бота сегодня {datetime.now().strftime("%d.%m.%Y")}")


@router.message(F.text == "Время")
async def current_time(
        message: Message,
) -> None:
    await message.answer(f"У бота сейчас на часах {datetime.now().strftime("%H:%M")}")
