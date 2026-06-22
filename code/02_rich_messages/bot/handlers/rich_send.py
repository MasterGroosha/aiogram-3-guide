from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InputRichMessage, Message

router = Router(name="rich_send")


REPORT_HTML = """\
<h1>Отчёт за квартал</h1>
<p>Небольшой пример того, как <b>Rich Messages</b> держат структуру: здесь есть \
заголовки разного уровня, таблица, формула и сноска<sup><a name="ref-1"></a><a href="#note-1">1</a></sup>.</p>
<h2>Ключевые метрики</h2>
<table>
<tr><th align="left">Метрика</th><th align="right">Было</th><th align="right">Стало</th></tr>
<tr><td align="left">MRR</td><td align="right">$35k</td><td align="right">$42k</td></tr>
<tr><td align="left">Активные чаты</td><td align="right">1 240</td><td align="right">1 510</td></tr>
<tr><td align="left">Отвалившиеся боты</td><td align="right">12</td><td align="right">7</td></tr>
</table>
<h2>Немного математики</h2>
<p>Прирост считаем по простой формуле:</p>
<tg-math-block>rate = (new - old) / old</tg-math-block>
<blockquote>Это блочная цитата. Внутри неё можно держать <i>курсив</i>, \
<code>код</code> и даже <tg-spoiler>спойлер</tg-spoiler>.</blockquote>

<footer>1. Цифры выдуманы для примера и ничего не отражают. <a name="note-1"></a><a href="#ref-1">↩️</a>️</footer>
"""


@router.message(Command("sendrich"))
async def cmd_send_rich(
        message: Message,
) -> None:
    # Поскольку мы заполнили поле html, Telegram трактует текст как Rich HTML.
    await message.answer_rich(
        rich_message=InputRichMessage(html=REPORT_HTML),
    )
