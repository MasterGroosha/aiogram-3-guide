# Обробники питань з клавіатурою Так/Ні
from aiogram import Router, F                           # Основні компоненти aiogram
from aiogram.filters import Command                     # Фільтри команд
from aiogram.types import Message, ReplyKeyboardRemove # Типи повідомлень та клавіатур

# Імпорт функції для створення клавіатури з окремого модуля
from keyboards.for_questions import get_yes_no_kb

# Створення роутера для обробників питань
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """
    Обробник команди /start - демонструє використання клавіатури з окремого модуля
    Показує як організувати код з роутерами та винесеними клавіатурами
    """
    await message.answer(
        "Чи задоволені ви своєю роботою?",
        reply_markup=get_yes_no_kb()
    )


@router.message(F.text.lower() == "так")
async def answer_yes(message: Message):
    """
    Обробник позитивної відповіді - приховує клавіатуру після відповіді
    """
    await message.answer(
        "Це чудово!",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(F.text.lower() == "ні")
async def answer_no(message: Message):
    """
    Обробник негативної відповіді - приховує клавіатуру після відповіді
    """
    await message.answer(
        "Шкода...",
        reply_markup=ReplyKeyboardRemove()
    )