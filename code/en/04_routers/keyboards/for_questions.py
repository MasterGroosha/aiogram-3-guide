# Import aiogram keyboard components
from aiogram.types import ReplyKeyboardMarkup            # Reply keyboard markup type
from aiogram.utils.keyboard import ReplyKeyboardBuilder  # Keyboard builder utility


def get_yes_no_kb() -> ReplyKeyboardMarkup:
    """
    Create a simple Yes/No keyboard for user responses
    
    Returns:
        ReplyKeyboardMarkup: A keyboard with Yes and No buttons in one row
    """
    # Create keyboard builder instance
    kb = ReplyKeyboardBuilder()
    
    # Add buttons with English text
    kb.button(text="Yes")
    kb.button(text="No")
    
    # Arrange buttons in a row (2 buttons per row)
    kb.adjust(2)
    
    # Return markup with resize_keyboard=True for better mobile experience
    return kb.as_markup(resize_keyboard=True)
