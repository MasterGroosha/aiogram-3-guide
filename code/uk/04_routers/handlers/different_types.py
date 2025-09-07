# Обробники різних типів повідомлень
from aiogram import Router, F        # Основні компоненти aiogram
from aiogram.types import Message    # Тип повідомлення

# Створення роутера для обробки різних типів контенту
router = Router()


@router.message(F.text)
async def message_with_text(message: Message):
    """
    Обробник текстових повідомлень
    Спрацьовує для будь-якого текстового повідомлення
    """
    await message.answer("Це текстове повідомлення!")


@router.message(F.sticker)
async def message_with_sticker(message: Message):
    """
    Обробник стікерів
    Спрацьовує при отриманні стікера від користувача
    """
    await message.answer("Це стікер!")


@router.message(F.animation)
async def message_with_gif(message: Message):
    """
    Обробник GIF-анімацій
    Спрацьовує при отриманні анімованого зображення
    """
    await message.answer("Це GIF!")