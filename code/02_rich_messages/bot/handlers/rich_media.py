from aiogram import Router
from aiogram.filters import Command
from aiogram.types import (
    FSInputFile,
    InputMediaPhoto,
    InputRichMessage,
    InputRichMessageMedia,
    Message,
)

router = Router(name="rich_media")

GALLERY_MARKDOWN = """\
# Галерея HTTP-котиков

Несколько картинок внутри одного богатого сообщения, у каждой — описание и подпись.

**204 No Content** — сервер успешно обработал запрос, но возвращать в теле ответа нечего. Клиент остаётся на текущей странице и при необходимости обновляет данные по заголовкам ответа.

![](https://http.cat/images/204.jpg "HTTP 204 No Content")

**301 Moved Permanently** — запрошенный ресурс окончательно переехал на новый адрес из заголовка `Location`. Все будущие запросы и закладки стоит направлять уже туда, а поисковики со временем обновят ссылки.

![](https://http.cat/images/301.jpg "HTTP 301 Moved Permanently")

**418 I'm a teapot** — шуточный код из первоапрельского RFC 2324: сервер-чайник наотрез отказывается заваривать кофе. В реальных API не используется, но живёт как любимая пасхалка.

![](https://http.cat/images/418.jpg "HTTP 418 I am a Teapot")

Под галереей можно спокойно продолжать текст: заголовки, списки и всё остальное
работают как обычно.
"""


CARD_MARKDOWN = """\
# Медиа из своего файла

Картинка ниже уехала в Telegram не по ссылке, а прямо с диска:
в тексте стоит только `tg://photo?id=logo`, а сам файл описан в поле `media`.

![](tg://photo?id=logo "Загружено с диска")
"""

# file_id привязан к конкретному боту: чужой здесь не сработает.
# Свой можно подсмотреть, отправив боту картинку и распечатав
# message.photo[-1].file_id
PHOTO_FILE_ID = (
    "AgACAgIAAxkBAANwao4JLwOy96vw-Ptu9j_eJvETAWcAArolaxsC_HBI"
    "tObSPMI6oF8BAAMCAAN4AAM9BA"
)

REUSE_MARKDOWN = """\
# Медиа по file_id

А эта картинка вообще никуда не загружалась: Telegram переиспользовал файл,
который у него уже лежит, по одному только `file_id`.

![](tg://photo?id=logo "Переиспользовано по file_id")
"""


@router.message(Command("sendrichmedia"))
async def cmd_send_rich_media(
        message: Message,
) -> None:
    await message.answer_rich(
        rich_message=InputRichMessage(markdown=GALLERY_MARKDOWN),
    )


@router.message(Command("sendrichmediafile"))
async def cmd_send_rich_media_file(
        message: Message,
) -> None:
    await message.answer_rich(
        rich_message=InputRichMessage(
            markdown=CARD_MARKDOWN,
            media=[
                InputRichMessageMedia(
                    # id — это то, что стоит в ссылке tg://photo?id=...
                    # 1-64 символа, только A-Z, a-z, 0-9, _ и -
                    id="logo",
                    # Файл с диска: aiogram сам соберёт multipart-запрос
                    media=InputMediaPhoto(media=FSInputFile("bot/assets/logo.png")),
                ),
            ],
        ),
    )


@router.message(Command("sendrichmediafileid"))
async def cmd_send_rich_media_file_id(
        message: Message,
) -> None:
    await message.answer_rich(
        rich_message=InputRichMessage(
            markdown=REUSE_MARKDOWN,
            media=[
                InputRichMessageMedia(
                    id="logo",
                    # Разница с примером выше — только здесь:
                    # вместо FSInputFile обычная строка с file_id
                    media=InputMediaPhoto(media=PHOTO_FILE_ID),
                ),
            ],
        ),
    )