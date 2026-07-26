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
        "/images — три способа загрузить изображение (буфер, файл, ссылка)\n"
        "/gif — подпись над анимацией\n"
        "/album — сборка альбома из нескольких фото\n\n"
        "А ещё пришлите боту фото, стикер или гифку — он их скачает или перешлёт обратно, "
        "а если добавите кого-то в группу — поприветствует новичка."
    )
