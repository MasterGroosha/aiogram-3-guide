# Функції для створення клавіатур питань
from aiogram.types import ReplyKeyboardMarkup           # Тип звичайної клавіатури
from aiogram.utils.keyboard import ReplyKeyboardBuilder # Будівельник клавіатур


def get_yes_no_kb() -> ReplyKeyboardMarkup:
    """
    Створює клавіатуру з кнопками "Так" та "Ні"
    
    Returns:
        ReplyKeyboardMarkup: Готова клавіатура з двома кнопками
    """
    # Використання будівельника для створення клавіатури
    kb = ReplyKeyboardBuilder()
    
    # Додавання кнопок з текстом
    kb.button(text="Так")
    kb.button(text="Ні")
    
    # Розташування кнопок: 2 кнопки в одному ряду
    kb.adjust(2)
    
    # Повернення готової клавіатури з автоматичним підлаштуванням розміру
    return kb.as_markup(resize_keyboard=True)