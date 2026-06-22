from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InputRichMessage, Message

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


@router.message(Command("sendrichmedia"))
async def cmd_send_rich_media(
        message: Message,
) -> None:
    await message.answer_rich(
        rich_message=InputRichMessage(markdown=GALLERY_MARKDOWN),
    )