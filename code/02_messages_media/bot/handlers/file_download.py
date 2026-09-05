from aiogram import Bot, F, Router
from aiogram.types import Message

router = Router(name="file_download")


@router.message(F.photo)
async def download_photo(message: Message, bot: Bot) -> None:
    await bot.download(
        message.photo[-1],
        destination=f"/tmp/{message.photo[-1].file_id}.jpg"
    )


@router.message(F.sticker)
async def download_sticker(message: Message, bot: Bot) -> None:
    await bot.download(
        message.sticker,
        # для Windows пути надо подправить
        destination=f"/tmp/{message.sticker.file_id}.webp"
    )
