---
title: Rich Messages
description: Rich Messages
---

# Rich Messages

!!! info ""
    Используемая версия aiogram: 3.29.0

Многие годы в Telegram существовало всего три способа форматировать сообщения: **plaintext**, т.е. без форматирования,
**HTML** и **Markdown** в двух вариантах, один из которых признан устаревшим. Когда планету охватил бум нейросетей, возможности 
украшения текста в мессенджере начали выглядеть довольно скупо. ChatGPT генерирует красивые таблицы, формулы 
и списки со сносками, а отобразить всё это в Telegram без костылей нельзя. Разработчики Bot API в обновлении 
Bot API 10.1 (июнь 2026г.) добавили фичу под названием Rich Messages, призванную решить данную проблему. 
В этой главе поговорим про эти Messages, насколько они Rich.

## Общая информация {: id="intro" }

Что же такое «богатые сообщения» (звучит кринжово, поэтому далее я буду называть их по-английски Rich Messages или RM)? 
Документация описывает их так:

> Rich Messages предназначены для сильно структурированных ответов: отчётов, ответов от ИИ, 
> документации, технических статей и другого подобного сложного контента.
> Такие сообщения поддерживают как Rich Markdown, так и Rich HTML. 
> Rich Markdown использует GitHub Flavored Markdown и может включать в себя поддерживаемые 
> HTML-теги прямо в том же сообщении. Rich HTML даёт ботам более точный контроль над ещё большим количеством 
> возможностей форматирования с помощью специальных тегов.

> Поддерживаемые стили включают:  
> - Заголовки, абзацы, разделители, списки и todo-листы.  
> - Вложенное inline-форматирование, включая жирный текст, курсив, подчёркивание, зачёркивание, спойлер, код, нижний и верхний регистр.  
> - Таблицы с выравниванием, подписями, границами, «полосатым» стилем, объединением колонок и объединением строк.  
> - Медиа-блоки для фотографий, видео и аудиофайлов, с подписями и указанием авторства.  
> - Блочные цитаты, выделенные цитаты, сворачиваемые блоки details, якоря и ссылки внутри документа.  
> - Сноски и текст, на который можно ссылаться.  
> - Полная поддержка LaTeX, включая как inline-формулы, так и блочные формулы.  
> - Карты с координатами, коллажи, слайд-шоу и многое другое.  

> **Ограничения Rich Messages**. На Rich Messages действуют следующие ограничения:  
> - До **32768** UTF-8 символов в тексте расширенного сообщения, включая альтернативный текст кастомных эмодзи и исходный код формулы.  
> - До **500** блоков, включая вложенные блоки, элементы списков, элементы нумерованных списков, строки таблиц, блоки цитат и блоки `details`.  
> - До **16** уровней вложенного форматирования и блоков.  
> - До **50** медиа-вложений всего, включая фотографии, видео и аудиофайлы.  
> - До **20** колонок в таблице.  

Выглядят RM действительно здорово. Если ещё не видели их в действии, то можете посмотреть красивую демку в 
[документации](https://core.telegram.org/bots/features#advanced-formatting-options) или в 
официальном демонстрационном боте [@richtextdemobot](https://telegram.dog/richtextdemobot).

## Отличие от обычных сообщений {: id="rich-vs-regular" }

Rich Messages **не заменяют** старый добрый `sendMessage` с MarkdownV2 и HTML. 
Это два разных инструмента под разные задачи:

* **Обычные сообщения** (`sendMessage`) — это лёгкий формат для коротких текстов: подтверждений ввода, реплик в диалоге, 
  пары строк с жирным словом и ссылкой. Здесь же остаются «эксклюзивные» возможности вроде частичного цитирования
  и пересылки цитаты в другой чат.

* **Rich Messages** (`sendRichMessage`) — хороший вариант, когда нужно отправить «сложный» текст: отчёт, документацию,
  длинный ответ от нейросети. Заголовки, таблицы, сноски, формулы, сворачиваемые блоки — всё то, ради чего раньше
  приходилось рендерить ответ картинкой через PIL или городить ASCII-арт. Такие сообщения при необходимости можно
  и отредактировать — [ниже](#editing) посмотрим, как именно.

Иными словами: если вам нужно отправить простое и короткое «Готово ✅» — это `sendMessage`. 
Если вам нужно отправить структурированный отчёт с таблицами и сносками на пол-экрана — это `sendRichMessage`.

Ещё важный момент, который стоит упомянуть до перехода к практической части: 
у RM не существует такого понятия как "parse mode": язык разметки зависит от того, какой именно аргумент 
функции вы выберите — `markdown` или `html`. Явное лучше неявного, да.

## Как отправить Rich Message {: id="how-to-send" }

В Bot API за отправку отвечает метод [sendRichMessage](https://core.telegram.org/bots/api#sendrichmessage),
а сам контент описывается объектом [InputRichMessage](https://core.telegram.org/bots/api#inputrichmessage).

Пример подготовки текста в двух разных языках разметки:

```python
from aiogram.types import InputRichMessage

# Вариант с Markdown
md_content = InputRichMessage(markdown="# Заголовок\n\nПривет, **мир**!")

# Вариант с HTML — то же самое, но другим синтаксисом
html_content = InputRichMessage(html="<h1>Заголовок</h1><p>Привет, <b>мир</b>!</p>")
```

Дальше этот объект можно отправить либо напрямую через `bot.send_rich_message(...)`, либо через привычные шорткаты
у `Message`: `answer_rich()` и `reply_rich()`

Соберём осмысленный пример, в котором задействованы заголовки разного уровня, таблица, формула и сноска. На этот раз
опишем сообщение через **Rich HTML** — для этого достаточно положить текст в поле `html`. Текст опишем
отдельной константой:

```python title="bot/handlers/rich_send.py"
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

<footer><a name="note-1"></a><a href="#ref-1">1.</a>Цифры выдуманы для примера и ничего не отражают. ↩️</footer>
"""


@router.message(Command("sendrich"))
async def cmd_send_rich(
        message: Message,
) -> None:
    await message.answer_rich(
        rich_message=InputRichMessage(html=REPORT_HTML),
    )
```

Что здесь происходит:

* Заголовки задаются привычными тегами `<h1>`…`<h6>`, абзацы — тегом `<p>`. 
* Сноска — настоящая интерактивная, работает в обе стороны на якорях. 
В тексте маркер это `<sup>`, внутри которого якорь `<a name="ref-1">` (точка возврата) и ссылка 
`<a href="#note-1">1</a>` на текст сноски. В футере (пункт 5) всё зеркально. 
Тег `<a>` с атрибутом name задаёт якорь, а `<a href="#имя">` — ссылка на него внутри сообщения 
(с пустым `<a href="#">` ссылка ведёт в начало).
* Таблица — это тег `<table>` со строками `<tr>` и ячейками `<td>`/`<th>` (заголовочные). 
Выравнивание задаётся атрибутом `align` (`left`/`center`/`right`), а для вертикального есть `valign`. 
Поддерживаются также `colspan`/`rowspan`, рамки и «полосатый» стиль.
* Блочная формула — кастомный тег `<tg-math-block>`, внутри обычный LaTeX. Telegram отрендерит формулу сам.
* Футер `<footer>` — здесь живёт текст сноски и обратная ссылка ↩️ к маркеру: якорь `<a name="note-1">` 
позволяет «прыгнуть» вниз к сноске, а ссылка `<a href="#ref-1">` возвращает наверх. 
* Внутри `<blockquote>`, видно, что inline-теги (`<i>`, `<code>`, `<tg-spoiler>`) работают и во вложенных блоках.
* Шорткат `answer_rich()` отправляет `InputRichMessage` в тот же чат. 
Поскольку мы заполнили поле `html`, Telegram трактует текст как Rich HTML.

Результат выглядит так: 

![Rich Message](images/rich-messages/sendrich_dark.png#only-dark){ width="600" }
![Rich Message](images/rich-messages/sendrich_light.png#only-light){ width="600" }

!!! warning "Не забывайте экранировать"
    Как и в обычном HTML-форматировании, символы `<`, `>` и `&`, не являющиеся частью тега, нужно заменять на
    `&lt;`, `&gt;` и `&amp;`. Иначе Telegram попытается принять кусок текста за тег и сломает разметку.

!!! tip "Markdown и HTML можно мешать"
    Rich Markdown разрешает вставлять поддерживаемые HTML-теги прямо внутрь markdown-текста. Это удобно, когда какой-то
    блок проще выразить тегом, а основной текст хочется держать в markdown. А если нужен полный контроль над всеми
    возможностями форматирования — берите целиком `html`-вариант, как мы сделали выше.

## Редактирование Rich Messages {: id="editing" }

Отправлять научились, теперь про редактирование. Отдельного метода вроде `editRichMessage` в Bot API не завезли:
вместо этого у [editMessageText](https://core.telegram.org/bots/api#editmessagetext) появился
аргумент `rich_message`. Аргументы `text` и `rich_message` взаимоисключающие: нужно передать ровно один из них.
В aiogram, соответственно, работает привычный шорткат `edit_text()`.

Соберём маленький пример: по команде `/sendrichedit` бот отправляет чек-лист релиза (todo-лист — как раз одна из
«фишек» RM) с инлайн-кнопкой, а по нажатию на кнопку отмечает все пункты выполненными:

```python title="bot/handlers/rich_edit.py"
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputRichMessage,
    Message,
)

router = Router(name="rich_edit")

CHECKLIST_BEFORE = """\
# Чек-лист релиза

Прогресс: **0 из 3**

- [ ] Прогнать тесты
- [ ] Обновить документацию
- [ ] Задеплоить бота
"""

CHECKLIST_AFTER = """\
# Чек-лист релиза

Прогресс: **3 из 3** 🎉

- [x] Прогнать тесты
- [x] Обновить документацию
- [x] Задеплоить бота
"""


@router.message(Command("sendrichedit"))
async def cmd_send_rich_edit(
        message: Message,
) -> None:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="Выполнить все пункты",
            callback_data="complete_checklist",
        )
    ]])
    await message.answer_rich(                                    # [1]
        rich_message=InputRichMessage(markdown=CHECKLIST_BEFORE),
        reply_markup=keyboard,
    )


@router.callback_query(F.data == "complete_checklist")
async def on_complete_checklist(
        callback: CallbackQuery,
) -> None:
    await callback.message.edit_text(                             # [2]
        rich_message=InputRichMessage(markdown=CHECKLIST_AFTER),  # [3]
    )
    await callback.answer()
```

По пунктам:

1. Шорткат `answer_rich()` принимает `reply_markup` точно так же, как обычный `answer()`: к Rich Message можно
   прикрутить любую инлайн-клавиатуру.
2. Редактирование — через знакомый по обычным сообщениям `edit_text()`. А поскольку мы не передали `reply_markup`,
   после редактирования кнопка исчезнет — все пункты выполнены, нажимать больше нечего.
3. Вместо аргумента `text` передаём `rich_message` с новым содержимым — обычный `InputRichMessage`, 
   точно такой же, как при отправке.

![Rich Message](images/rich-messages/sendrichedit_dark.png#only-dark){ width="500" }
![Rich Message](images/rich-messages/sendrichedit_light.png#only-light){ width="500" }

## Стриминг через `sendRichMessageDraft` {: id="streaming" }

Поговорим про стриминг текста. В одном из прошлых обновлений завезли `sendMessageDraft` для обычных сообщений, 
аналогичный метод существует и для Rich Messages. Вообще, про стриминг уже было достаточно подробно написано 
[в отдельной заметке](blog/posts/project_threads_llm.md#_3), но стоит повторить общие принципы ещё раз.

Работает стриминг так:

* Метод показывает пользователю **черновик** — временное превью сообщения. Этот черновик эфемерный: он живёт около
  30 секунд и сам растворяется, в истории чата не остаётся.
* У черновика есть `draft_id` — ненулевой идентификатор. Все апдейты с одним и тем же `draft_id` Telegram анимирует
  как плавное изменение одного и того же черновика, без мигания.
* Когда генерация закончена, черновик нужно «зафиксировать»: отправить готовое сообщение обычным `sendRichMessage`.

```python title="bot/handlers/rich_stream.py"
import asyncio
from random import randint

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import InputRichMessage, Message

router = Router(name="rich_stream")

# Финальный текст, который мы будем печатать по кусочкам.
FINAL_MARKDOWN = """\
# Что такое стриминг черновика

Метод `sendRichMessageDraft` показывает пользователю **временное превью**
сообщения, пока оно ещё генерируется — ровно так ведут себя нейросетевые
ассистенты, печатающие ответ постепенно.

## Как это работает

- Черновик **эфемерный**: он живёт около 30 секунд и сам исчезает.
- Все апдейты с одним и тем же `draft_id` Telegram анимирует как плавную правку.
- Чтобы сообщение осталось в чате насовсем, в конце нужно отправить его
  обычным `sendRichMessage`.
"""


def _build_chunks(text: str) -> list[str]:                        # [1]
    words = text.split(" ")
    chunks: list[str] = []
    step = 12
    for i in range(step, len(words), step):
        chunks.append(" ".join(words[:i]))
    chunks.append(text)
    return chunks

@router.message(Command("sendrichstream"))
async def cmd_send_rich_stream(
        message: Message,
        bot: Bot,
) -> None:
    # Генерируем случайный айди черновика
    draft_id = randint(1, 100_000_000)                            # [2]

    # Имитируем первичную задержку перед «первым токеном»:
    # покажем заглушку для пустого текста и выждем паузу в 2 секунды.
    await bot.send_rich_message_draft(                            # [3]
        chat_id=message.chat.id,
        draft_id=draft_id,
        rich_message=InputRichMessage(
            markdown="<tg-thinking>Думаю...</tg-thinking>"        # [4]
        ),
    )
    await asyncio.sleep(2.0)

    for chunk in _build_chunks(FINAL_MARKDOWN):
        await bot.send_rich_message_draft(
            chat_id=message.chat.id,
            draft_id=draft_id,
            rich_message=InputRichMessage(markdown=chunk),
        )
        await asyncio.sleep(0.7)                                  # [5]
    await message.answer_rich(                                    # [6]
        rich_message=InputRichMessage(markdown=FINAL_MARKDOWN),
    )
```

По пунктам:

1. В учебных целях мы режем итоговый текст на нарастающие префиксы. В настоящем боте на их месте были бы токены 
от LLM, которые вы накапливаете в буфер и периодически отправляете черновиком.
2. `draft_id` должен быть ненулевым. Используем случайное число в качестве такого идентификатора.
3. Собственно отправка очередного куска. Обратите внимание, что метод возвращает `True`/`False`, \
а не объект `Message` — это ведь не настоящее сообщение, а превью.
4. Заглушка, которую можно показывать, пока вообще никакого текста нет. Красиво анимировано, кстати.
5. Небольшая пауза между апдейтами, чтобы не упереться в флуд-лимиты. Подбирайте интервал под свою нагрузку.
6. Финал: отправляем полный текст обычным `answer_rich()`. Вот это сообщение уже останется в чате.

!!! note "Не пытайтесь стримить посимвольно"
    Каждый вызов `send_rich_message_draft` — это сетевой запрос. Накопите разумный буфер (несколько слов или строку)
    и отправляйте превью раз в несколько сотен миллисекунд, иначе Telegram быстро прижмёт вас лимитами.

Как это выглядит «в динамике» на видео:

![type:video](images/rich-messages/streaming_dark.mp4)

## Медиафайлы {: id="media" }

Текстом дело не ограничивается — внутрь RM можно встраивать медиа. Здесь всплывает неприятная особенность 
Rich Messages: медиафайлы нельзя передавать по `file_id`, только по HTTP(S)-ссылкам. 

В Rich Markdown для медиафайлов поддерживается стандартный Markdown-синтаксис: `![alt-текст](URL "title")`. Однако 
часть с alt-текстом (в обычном вебе он используется в случае, когда медиафайл не загрузился или в режиме «только текст») 
в Telegram нигде не отображается, а видимую подпись нужно задавать сразу после URL в кавычках. 
Впрочем, посмотрите пример ниже и всё поймёте:

```python title="bot/handlers/rich_media.py"
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
```

Верхняя часть готового сообщения на скриншоте:

![Rich Message](images/rich-messages/sendrichmedia_dark.png#only-dark){ width="500" } 
![Rich Message](images/rich-messages/sendrichmedia_light.png#only-light){ width="500" } 

!!! note "Коллаж, слайд-шоу и прочее медиа"
    Несколько изображений подряд — это базовый случай. Для тонкого управления компоновкой в Rich HTML есть отдельные
    теги: `<photo>`, `<video>` и `<audio>` для одиночных медиа, а также кастомные `<tg-collage>` (коллаж) и
    `<tg-slideshow>` (слайд-шоу), внутрь которых вкладываются медиа-блоки. Пощупать рендеринг вживую можно в
    [@richtextdemobot](https://telegram.dog/richtextdemobot).


## Как поймать и разобрать Rich Message {: id="parsing" }

Помимо отправки Rich Messages, нужно научиться их принимать и «понимать». Тем более, что одними из первых, 
кто освоили новый тип сообщений, стали спамеры. У класса [Message](https://core.telegram.org/bots/api#message)
появилось новое поле `rich_message` типа [RichMessage](https://core.telegram.org/bots/api#richmessage). Оно заполняется,
когда боту прилетает RM.

Устроен `RichMessage` просто: это список блоков (`blocks`). Каждый блок имеет общее поле `type` (`heading`, `paragraph`,
`table`, `list`, `photo`, `slideshow`, `collage`, `footer` и т.д.), а текстовые блоки несут в поле `text` дерево из объектов
`RichText`. Это дерево может быть строкой, списком узлов или стилизованным узлом (жирный, курсив...), внутри которого снова
лежит `RichText`. Чтобы достать из него «голый» текст, удобно написать маленькую рекурсивную функцию:

```python title="bot/handlers/rich_parse.py"
from collections import Counter

from aiogram import F, Router
from aiogram.types import Message

router = Router(name="rich_parse")


def flatten_text(node) -> str:
    if node is None:
        return ""
    if isinstance(node, str):                                     # [1]
        return node
    if isinstance(node, list):                                    # [2]
        return "".join(flatten_text(item) for item in node)
    # У кастомных эмодзи нет вложенного text, зато есть альтернативный текст
    if getattr(node, "type", None) == "custom_emoji":             # [3]
        return node.alternative_text
    return flatten_text(getattr(node, "text", None))              # [4]


@router.message(F.rich_message)                                   # [5]
async def on_rich_message(
        message: Message,
) -> None:
    blocks = message.rich_message.blocks

    stats = "\n".join(f"• {block.type}" for block in blocks)      # [6]

    headings = [                                                  # [7]
        flatten_text(block.text)
        for block in blocks
        if block.type == "heading"
    ]

    table = next((b for b in blocks if b.type == "table"), None)  # [8]

    lines = [
        f"Rich Message из {len(blocks)} блоков.",
        f"Состав: {stats}",
    ]
    if headings:
        toc = "\n".join(f"• {title}" for title in headings)
        lines.append(f"\nЗаголовки:\n{toc}")
    if table is not None:
        first_row = " | ".join(flatten_text(cell.text) for cell in table.cells[0])
        lines.append(f"\nПервая строка таблицы: {first_row}")

    await message.answer("\n".join(lines))
```

Разберём ключевые места:

1. Базовый случай рекурсии: если узел — обычная строка, возвращаем её как есть.
2. Если узел — список, склеиваем результат обхода каждого элемента.
3. У кастомного эмодзи нет вложенного `text`, зато есть `alternative_text` — берём его.
4. Во всех остальных случаях это стилизованный узел: спускаемся в его поле `text` ещё на уровень глубже.
5. Магический фильтр `F.rich_message` срабатывает, только если у входящего сообщения заполнено поле `rich_message`. 
   Так мы ловим именно богатые сообщения и не мешаем командам.
6. Собираем блоки в порядке их появления.
7. Собираем все заголовки в оглавление. Заодно видно, как `flatten_text` вытаскивает текст из заголовка, 
   даже если он обёрнут в курсив или жирный.
8. Если внутри есть таблица, достаём её первую строку. Ячейки лежат в `table.cells` как список списков (`строки → ячейки`), 
   а текст ячейки — снова дерево RichText.

Если переслать боту его же собственный пример с HTTP-котиками, то вы должны увидеть следующее сообщение:

```
Rich Message из 9 блоков.
Состав:
• heading
• paragraph
• paragraph
• photo
• paragraph
• photo
• paragraph
• photo
• paragraph

Заголовки:
• Галерея HTTP-котиков
```


## Заключение {: id="conclusion" }

Rich Messages — это давно напрашивавшийся ответ Telegram на эпоху нейросетей и повсеместного использования Markdown.
В этой главе мы научились отправлять такие сообщения (через `markdown`/`html`), редактировать их, разбирать входящие 
по блокам и стримить ответы через эфемерные черновики. За кадром осталось ещё много блоков — карты, сворачиваемые `details`,
аудио и видео, блочные формулы — но принцип везде один и тот же, так что вооружившись основами, остальное вы освоите
по [документации](https://core.telegram.org/bots/api#inputrichmessage) и [демо-боту](https://telegram.dog/richtextdemobot).
