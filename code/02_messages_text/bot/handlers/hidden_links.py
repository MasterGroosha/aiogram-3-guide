from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, LinkPreviewOptions
from aiogram.utils.markdown import hide_link

router = Router(name="hidden_links")


@router.message(Command("hidden_link"))
async def cmd_hidden_link(message: Message) -> None:
    await message.answer(
        f"{hide_link('https://telegra.ph/file/562a512448876923e28c3.png')}"
        f"Документация Telegram: *существует*\n"
        f"Пользователи: *не читают документацию*\n"
        f"Груша:"
    )


@router.message(Command("hidden_link2"))
async def cmd_hidden_link2(message: Message) -> None:
    link_preview = LinkPreviewOptions(
        url="https://images.meme-arsenal.com/486c03d2bb9d2ef7588f8f16c282579a.jpg",
        prefer_large_media=True
    )
    await message.answer(
        f"Bot API: *обновляется*\n"
        f"Груша: *игнорирует*\n"
        f"Bot API: *обновляется ещё 100500 раз*\n"
        f"Груша:",
        link_preview_options=link_preview
    )
