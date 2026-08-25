from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    BufferedInputFile, FSInputFile, Message, URLInputFile,
)

router = Router(name="file_upload")


@router.message(F.animation)
async def echo_gif(message: Message) -> None:
    await message.reply_animation(message.animation.file_id)


@router.message(Command('images'))
async def upload_photo(message: Message) -> None:
    # Сюда будем помещать file_id отправленных файлов, чтобы потом ими воспользоваться
    file_ids = []

    # Чтобы продемонстрировать BufferedInputFile, воспользуемся "классическим"
    # открытием файла через `open()`. Но, вообще говоря, этот способ
    # лучше всего подходит для отправки байтов из оперативной памяти
    # после проведения каких-либо манипуляций, например, редактированием через Pillow
    with open("buffer_emulation.jpg", "rb") as image_from_buffer:
        result = await message.answer_photo(
            BufferedInputFile(
                image_from_buffer.read(),
                filename="image from buffer.jpg"
            ),
            caption="Изображение из буфера"
        )
        file_ids.append(result.photo[-1].file_id)

    # Отправка файла из файловой системы
    image_from_pc = FSInputFile("image_from_pc.jpg")
    result = await message.answer_photo(
        image_from_pc,
        caption="Изображение из файла на компьютере"
    )
    file_ids.append(result.photo[-1].file_id)

    # Отправка файла по ссылке
    image_from_url = URLInputFile("https://picsum.photos/seed/groosha/400/300")
    result = await message.answer_photo(
        image_from_url,
        caption="Изображение по ссылке"
    )
    file_ids.append(result.photo[-1].file_id)
    await message.answer("Отправленные файлы:\n" + "\n".join(file_ids))


@router.message(Command("gif"))
async def send_gif(message: Message) -> None:
    await message.answer_animation(
        animation="<file_id гифки>",
        caption="Я сегодня:",
        show_caption_above_media=True
    )
