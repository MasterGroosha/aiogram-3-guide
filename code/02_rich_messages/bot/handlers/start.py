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
        "/sendrich — отправить Rich HTML-сообщение с таблицей и формулой\n"
        "/sendrichblocks — тот же отчёт, но собранный из блоков\n"
        "/sendrichbuttons — карточка релиза с кнопками внутри сообщения\n"
        "/sendrichedit — отправить редактируемый чек-лист с кнопкой\n"
        "/sendricheditblocks — чек-лист на блоках, по одному пункту за нажатие\n"
        "/sendrichstream — показать стриминг черновика Rich-сообщения\n"
        "/sendrichstreamstop — то же самое, но с кнопкой остановки генерации\n"
        "/sendrichmedia — отправить галерею HTTP-котиков\n"
        "/sendrichmediafile — отправить картинку с диска внутри Rich Message\n"
        "/sendrichmediafileid — то же самое, но по file_id\n"
        "/sendrichdoc — приложить документ с диска внутрь Rich Message\n\n"
        "Также можно переслать боту любой rich message — он его разберёт по кусочкам."
    )
