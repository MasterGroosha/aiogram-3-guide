from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router(name="start")


@router.message(CommandStart(deep_link=False))
async def cmd_start(
        message: Message,
) -> None:
    await message.answer(
        "Привет! Вот что умеет этот бот:\n\n"
        "/test — примеры разных parse_mode\n"
        "/hello — приветствие с безопасной подстановкой имени\n"
        "/advanced_example — сложное форматирование через utils.formatting\n"
        "/settimer <время> <текст> — разбор аргументов команды\n"
        "/custom1, /custom2 — команды с нестандартным префиксом\n"
        "/help или /start help — диплинк на справку\n"
        "/start book_123 — диплинк с параметром\n"
        "/links — варианты предпросмотра ссылок\n"
        "/hidden_link — скрытая ссылка в тексте\n\n"
        "А ещё пришлите любой текст — бот попробует найти в нём ссылку, "
        "e-mail или моноширинный фрагмент."
    )
