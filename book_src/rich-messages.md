---
title: Rich Messages
description: Rich Messages
---

# Rich Messages

!!! info ""
    Используемая версия aiogram: 3.31.0

Многие годы в Telegram существовало всего три способа форматировать сообщения: **plaintext**, т.е. без форматирования,
**HTML** и **Markdown** в двух вариантах, один из которых признан устаревшим. Когда планету охватил бум нейросетей, возможности 
украшения текста в мессенджере начали выглядеть довольно скупо: ChatGPT генерирует красивые таблицы, формулы 
и списки со сносками, а отобразить всё это в Telegram без костылей нельзя. Разработчики Bot API в обновлении 
Bot API 10.1 (июнь 2026г.) добавили фичу под названием Rich Messages, призванную решить данную проблему.
В этой главе поговорим про эти Messages, насколько они Rich.

![Мем для затравки](images/rich-messages/zoey_vekselstein_meme.png){ loading=lazy }

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
у RM не существует такого понятия как "parse mode". Способ описания сообщения зависит от того, какое именно поле 
объекта вы заполните, а полей этих три: `markdown`, `html` и `blocks`. Причём заполнить нужно ровно одно 
из трёх — так прямо и написано в документации: «Exactly **one** of the fields *html*, *markdown*, or *blocks* 
must be used». Первые два — это знакомая текстовая разметка, а третье, появившееся в Bot API 10.2, — 
список блоков-объектов вообще без какой-либо разметки. Явное лучше неявного, да, а `blocks` — это уже 
предельно явное описание структуры; про него будет [отдельный раздел](#blocks).

## Как отправить Rich Message {: id="how-to-send" }

В Bot API за отправку отвечает метод [sendRichMessage](https://core.telegram.org/bots/api#sendrichmessage),
а сам контент описывается объектом [InputRichMessage](https://core.telegram.org/bots/api#inputrichmessage).

Пример подготовки одного и того же текста всеми тремя способами:

```python
from aiogram.types import InputRichMessage, InputRichBlockParagraph

# Вариант с Markdown
md_content = InputRichMessage(
    markdown="# Заголовок\n\nПривет, **мир**!"
)

# Вариант с HTML — то же самое, но другим синтаксисом
html_content = InputRichMessage(
    html="<h1>Заголовок</h1><p>Привет, <b>мир</b>!</p>"
)

# Вариант с блоками — вообще без разметки, см. раздел «Блоки вместо разметки»
blocks_content = InputRichMessage(
    blocks=[InputRichBlockParagraph(text="Привет!")]
)
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
<table bordered striped compact>
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

<footer>1. Цифры выдуманы для примера и ничего не отражают. <a name="note-1"></a><a href="#ref-1">↩️</a></footer>
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
Поддерживаются также `colspan`/`rowspan`. А внешний вид таблицы включается атрибутами-флагами 
у самого `<table>`, без значений: `bordered` рисует рамки, `striped` делает «зебру», а `compact` 
(приехал в Bot API 10.3) поджимает отступы внутри ячеек. Именно они и делают таблицу нарядной, 
как на скриншоте ниже. Подпись к таблице задаётся вложенным тегом `<caption>`.
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

Напоследок — про пару полей `InputRichMessage`, которые в примере выше не участвовали, но об которые 
спотыкаются чуть ли не первым делом. Telegram самостоятельно ищет в тексте сущности и подсвечивает их, 
даже если вы ни о чём таком не просили: ссылки, e-mail, @юзернеймы, #хештеги, $кэштеги, /команды, номера 
телефонов и банковских карт. Иногда это ровно то, что нужно, а иногда совсем нет — особенно если текст 
приехал от нейросети и в нём то `/reset` из примера кода превращается в команду, то выдуманная моделью 
ссылка становится кликабельной. Отключается всё это одним флагом:

```python
InputRichMessage(
    markdown=SOME_TEXT,
    # Не подсвечивать ссылки, юзернеймы, хештеги и прочее автоматически
    skip_entity_detection=True,
)
```

## Блоки вместо разметки {: id="blocks" }

А теперь про третий способ, появившийся в Bot API 10.2. Вместо строки с тегами в `InputRichMessage` можно передать 
поле `blocks` — список объектов, каждый из которых описывает один структурный элемент сообщения: абзац, заголовок, 
таблицу, список, цитату. Никакой разметки, никакого парсинга на стороне Telegram.

Зачем это нужно, когда есть markdown и HTML:

* **Не надо экранировать.** Предыдущий раздел заканчивался предупреждением про `<`, `>` и `&` — так вот, к блочному 
  режиму оно просто не относится. Текст, который вы кладёте в `text`, физически не может сломать разметку, потому 
  что разметки там нет. Если вы вставляете в сообщение пользовательский ввод или ответ внешнего API — это главный аргумент.
* **Ошибку ловит pydantic, а не Telegram.** Забыли обязательное поле или перепутали тип — увидите ошибку прямо в IDE, 
  а не `400 Bad Request` в ответ на запрос.
* **Сообщение удобно генерировать программно.** Таблица собирается циклом по строкам данных, а не конкатенацией 
  строк с `<tr>`. Ниже как раз такой пример.

Обратная сторона тоже есть: блоки заметно многословнее. Если сообщение — это заголовок и пара абзацев, 
написанных вами руками, то разметка по-прежнему быстрее и читаемее, и городить ради неё пять строк 
конструкторов незачем. Выбирайте инструмент под задачу — ровно как и в случае с `sendMessage` 
против `sendRichMessage`.

### Как это устроено {: id="blocks-basics" }

Несколько вещей, которые полезно знать до первого примера:

* Поле `type` у блоков заполнять **не нужно**: у каждого класса оно уже проставлено дефолтом. Пишем 
  `InputRichBlockSectionHeading(text="Заголовок", size=1)`, а не `type="heading"`.
* Текст внутри блоков — это `RichText`, тот же самый тип, что мы будем разбирать 
  [в разделе про парсинг](#parsing). Он может быть обычной строкой, списком узлов или стилизованным узлом, 
  внутри которого снова лежит `RichText`. То есть вложенное форматирование выглядит так: 
  `text=["Обычный ", RichTextBold(text="жирный"), "."]`.
* У заголовка `size` — это число от 1 до 6, где 1 — самый крупный (аналог `<h1>`). Поле обязательное.

И три момента, на которых легко споткнуться:

!!! warning "Грабли блочного режима"
    * **Таблица.** У `RichBlockTableCell` поля `align` и `valign` — **обязательные, без дефолтов**, 
      их придётся указать в каждой ячейке (`align`: `left`/`center`/`right`, `valign`: `top`/`middle`/`bottom`). 
      Обратите внимание на имя класса: `RichBlockTableCell` **без** префикса `Input` — он общий для отправки и приёма.
    * **Список.** `InputRichBlockListItem.blocks` — это список блоков, а не текст. Пункт списка описывается не строкой, 
      а, например, `[InputRichBlockParagraph(text="...")]`.
    * **Медиа-блоки.** Их `caption` — это не строка, а объект `RichBlockCaption(text=..., credit=...)`, где `credit` 
      отвечает за указание авторства. При этом поле `caption` у вложенных `InputMediaPhoto`/`InputMediaVideo` 
      игнорируется: подпись задаётся только через `RichBlockCaption`.

### Каталог блоков {: id="blocks-catalog" }

| Класс | Что это | Ключевые поля |
|---|---|---|
| `InputRichBlockParagraph` | абзац `<p>` | `text` |
| `InputRichBlockSectionHeading` | заголовок `<h1>`…`<h6>` | `text`, `size` (1-6) |
| `InputRichBlockPreformatted` | блок кода `<pre><code>` | `text`, `language` |
| `InputRichBlockList` | список `<ul>`/`<ol>` | `items` |
| `InputRichBlockListItem` | пункт списка | `blocks`, `has_checkbox`, `is_checked`, `value`, `type` |
| `InputRichBlockTable` | таблица `<table>` | `cells`, `is_bordered`, `is_striped`, `is_compact`, `caption` |
| `InputRichBlockBlockQuotation` | цитата `<blockquote>` | `blocks`, `credit` |
| `InputRichBlockPullQuotation` | выделенная цитата по центру | `text`, `credit` |
| `InputRichBlockExpandableBlockQuotation` | разворачиваемая цитата | `text`, `credit` |
| `InputRichBlockDetails` | сворачиваемый блок `<details>` | `summary`, `blocks`, `is_open` |
| `InputRichBlockButtons` | ряд кнопок `<tg-button-row>` | `buttons` (1-8), `align` |
| `InputRichBlockDivider` | разделитель `<hr>` | — |
| `InputRichBlockFooter` | футер `<footer>` | `text` |
| `InputRichBlockAnchor` | якорь `<a name="...">` | `name` |
| `InputRichBlockMathematicalExpression` | блочная формула LaTeX | `expression` |
| `InputRichBlockPhoto` / `Video` / `Animation` / `Audio` / `VoiceNote` | медиа | одноимённое поле + `caption` |
| `InputRichBlockDocument` | файл `<tg-document>` | `document`, `caption` |
| `InputRichBlockCollage` / `InputRichBlockSlideshow` | коллаж / слайд-шоу | `blocks`, `caption` |
| `InputRichBlockMap` | карта | `location`, `zoom`, `width`, `height`, `caption` |
| `InputRichBlockThinking` | плейсхолдер «Думаю…» | `text`, только для [черновиков](#streaming) |

Пара уточнений по редким блокам. У `InputRichBlockMap` есть ограничения: `zoom` в диапазоне 0-24, `width` 
и `height` — 0-10000, при этом их сумма не должна превышать 10000, а соотношение сторон — 20:1. 
А у `InputRichBlockListItem` поле `type` (не путать с `type` самого блока!) задаёт тип метки нумерованного списка: 
`"a"`, `"A"`, `"i"`, `"I"` или `"1"`; числовое значение метки лежит в `value`. Отдельного флага «нумерованный список» 
в API нет — список становится нумерованным именно за счёт `value`/`type` у его элементов. И ещё одно, про свежий 
`InputRichBlockExpandableBlockQuotation`: несмотря на родство имён с `InputRichBlockBlockQuotation`, содержимое 
у него лежит в `text`, а не в `blocks` — по форме он ближе к `InputRichBlockPullQuotation`.

### Пример: тот же отчёт, но из блоков {: id="blocks-example" }

Чтобы сравнение было честным, соберём блоками ровно тот же отчёт за квартал, который выше был написан на Rich HTML. 
Откройте два файла рядом — результат в чате будет одинаковый.

Начнём с таблицы, потому что именно она лучше всего показывает смысл затеи. Данные лежат отдельно, 
а ячейки строятся циклом:

```python title="bot/handlers/rich_blocks.py"
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import (
    InputRichBlockBlockQuotation,
    InputRichBlockDivider,
    InputRichBlockFooter,
    InputRichBlockMathematicalExpression,
    InputRichBlockParagraph,
    InputRichBlockSectionHeading,
    InputRichBlockTable,
    InputRichMessage,
    Message,
    RichBlockTableCell,
    RichTextAnchor,
    RichTextAnchorLink,
    RichTextBold,
    RichTextCode,
    RichTextItalic,
    RichTextSpoiler,
    RichTextSuperscript,
)

router = Router(name="rich_blocks")

# Данные для таблицы: (метрика, было, стало)
METRICS = [
    ("MRR", "$35k", "$42k"),
    ("Активные чаты", "1 240", "1 510"),
    ("Отвалившиеся боты", "12", "7"),
]


def build_metrics_table() -> InputRichBlockTable:
    # align и valign у RichBlockTableCell — обязательные поля, без дефолтов
    header = [
        RichBlockTableCell(text="Метрика", align="left", valign="middle", is_header=True),
        RichBlockTableCell(text="Было", align="right", valign="middle", is_header=True),
        RichBlockTableCell(text="Стало", align="right", valign="middle", is_header=True),
    ]
    rows = [
        [
            RichBlockTableCell(text=name, align="left", valign="middle"),
            RichBlockTableCell(text=before, align="right", valign="middle"),
            RichBlockTableCell(text=after, align="right", valign="middle"),
        ]
        for name, before, after in METRICS
    ]
    return InputRichBlockTable(
        cells=[header, *rows],
        is_bordered=True,
        is_striped=True,
        is_compact=True,
    )
```

Добавьте в `METRICS` четвёртую строку — и таблица вырастет сама. С HTML-константой пришлось бы либо руками 
дописывать `<tr>`, либо склеивать теги в цикле и надеяться, что в данных не встретится символ `<`.

А `is_bordered`, `is_striped` и `is_compact` — это ровно те же рамки, «зебра» и поджатые отступы, 
что и атрибуты `bordered`/`striped`/`compact` у HTML-тега `<table>` выше. Такая пара «поле блока ↔ атрибут тега» 
есть почти у каждой настройки, так что перенести уже написанный HTML на блоки обычно получается механически.

Теперь само сообщение целиком:

```python title="bot/handlers/rich_blocks.py"
def build_report() -> InputRichMessage:
    return InputRichMessage(blocks=[
        # size=1 — самый крупный заголовок, аналог <h1>
        InputRichBlockSectionHeading(text="Отчёт за квартал", size=1),
        InputRichBlockParagraph(text=[                                 # [1]
            "Тот же самый отчёт, что и в ",
            RichTextCode(text="/sendrich"),
            ", но собранный из ",
            RichTextBold(text="блоков"),
            " — без единого тега и без экранирования",
            # Сноска: якорь-точка возврата и ссылка на текст сноски в футере
            RichTextSuperscript(text=[                                 # [2]
                RichTextAnchor(name="ref-1"),
                RichTextAnchorLink(text="1", anchor_name="note-1"),
            ]),
            ".",
        ]),
        InputRichBlockSectionHeading(text="Ключевые метрики", size=2),
        build_metrics_table(),                                         # [3]
        InputRichBlockSectionHeading(text="Немного математики", size=2),
        InputRichBlockParagraph(text="Прирост считаем по простой формуле:"),
        InputRichBlockMathematicalExpression(                          # [4]
            expression="rate = (new - old) / old",
        ),
        InputRichBlockBlockQuotation(                                  # [5]
            blocks=[
                InputRichBlockParagraph(text=[
                    "Это блочная цитата. Внутри неё можно держать ",
                    RichTextItalic(text="курсив"),
                    ", ",
                    RichTextCode(text="код"),
                    " и даже ",
                    RichTextSpoiler(text="спойлер"),
                    ".",
                ]),
            ],
            credit="Отдел аналитики",
        ),
        InputRichBlockDivider(),
        InputRichBlockFooter(text=[
            "1. Цифры выдуманы для примера и ничего не отражают. ",
            RichTextAnchor(name="note-1"),
            RichTextAnchorLink(text="↩️", anchor_name="ref-1"),
        ]),
    ])


@router.message(Command("sendrichblocks"))
async def cmd_send_rich_blocks(
        message: Message,
) -> None:
    # Заполнено поле blocks, поэтому markdown и html передавать нельзя:
    # ровно одно из трёх полей.
    await message.answer_rich(
        rich_message=build_report(),
    )
```

По пунктам:

1. Вот оно, вложенное форматирование: `text` принимает список, в котором вперемешку лежат обычные строки 
   и стилизованные узлы `RichText*`.
2. Та же сноска, что была в HTML-варианте, только собранная из объектов: `RichTextAnchor` — это точка возврата 
   (аналог `<a name="...">`), а `RichTextAnchorLink` — ссылка на якорь внутри сообщения (аналог `<a href="#...">`). 
   Кстати, `anchor_name=""` вернёт читателя в самое начало сообщения.
3. Блоки — обычные объекты, поэтому их спокойно можно собирать функциями и переиспользовать. 
   Со строковой константой так не получится.
4. Обратите внимание: у формулы поле называется `expression` и принимает строку LaTeX, а не `text`.
5. Цитата содержит не текст, а **вложенные блоки** — та же история, что и с пунктами списка. 
   Поле `credit` отвечает за указание авторства.


!!! note "Приём и отправка почти зеркальны"
    Классы `RichBlock*` (входящие) и `InputRichBlock*` (исходящие) устроены практически одинаково, а `RichText`, 
    `RichBlockCaption` и `RichBlockTableCell` вообще общие для обеих сторон — префикса `Input` у них нет именно 
    поэтому. Практический вывод: пойманное ботом Rich Message теперь можно почти механически пересобрать 
    в исходящее, поправив пару блоков. До появления `blocks` пришлось бы рендерить разобранное дерево 
    обратно в HTML-строку.

## Кнопки внутри сообщения {: id="buttons" }

До Bot API 10.3 кнопки к Rich Message прикручивались ровно так же, как к обычному сообщению: объектом 
`reply_markup`, отдельной клавиатурой снизу. Работало это нормально, но в длинном структурированном сообщении 
кнопка, живущая где-то под текстом, — так себе идея: пока читатель доскроллит до неё, он уже забудет, 
к какому именно пункту она относилась. В 10.3 кнопки можно вставлять внутрь тела сообщения, 
ровно там, где они нужны.

Способов два. Первый — блок [InputRichBlockButtons](https://core.telegram.org/bots/api#inputrichblockbuttons): 
ряд из 1-8 кнопок с необязательным `align` (`left`, `center` или `right`). Таких рядов в сообщении может быть 
сколько угодно и в любом месте: между абзацами, после таблицы, в самом конце. HTML-двойник — кастомный тег 
`<tg-button-row>`. Второй способ — [RichTextButton](https://core.telegram.org/bots/api#richtextbutton): 
кнопка прямо в потоке текста. Это обычный rich-text-узел, который лежит в `text` любого блока наравне 
с `RichTextBold` и остальными; в Rich HTML ему соответствует тег `<tg-button>` внутри `<p>`.

Сама кнопка — объект [RichMessageButton](https://core.telegram.org/bots/api#richmessagebutton), и он почти 
дословно повторяет знакомый по обычным клавиатурам `InlineKeyboardButton`: `url`, `callback_data`, `web_app`, 
`login_url`, `switch_inline_query` во всех трёх вариантах, `copy_text`. Как и там, заполнить нужно ровно одно 
из этих полей. Отличий, по сути, два. Во-первых, появился `style` — `"danger"`, `"success"`, `"primary"` 
или `"link"` (последний рисует кнопку простой ссылкой без рамки и разрешён **только** для callback-кнопок). 
Клиент подберёт цвета под свою тему сам. Во-вторых, есть `disabled`: положите туда пустой объект 
`DisabledButton()` — и кнопка останется на месте, но нажать её будет нельзя.

Обратите внимание на имя класса: `RichMessageButton` — **без** префикса `Input`. Он общий для отправки и приёма, 
ровно как уже знакомый по этой главе `RichBlockTableCell`.

!!! warning "Важно"
    Поле `text` у кнопки — это `RichText`, но с сильно урезанным набором узлов: разрешены только обычный текст, 
    `RichTextCustomEmoji` и `RichTextDateTime`. Жирный, курсив, код и всё остальное внутрь кнопки положить 
    не получится.

Соберём карточку релиза, которую бот присылает дежурному в пятницу вечером:

```python title="bot/handlers/rich_buttons.py"
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    CopyTextButton,
    DisabledButton,
    InputRichBlockButtons,
    InputRichBlockParagraph,
    InputRichBlockSectionHeading,
    InputRichMessage,
    Message,
    RichMessageButton,
    RichTextButton,
)

router = Router(name="rich_buttons")

RELEASE = "v4.2.0"


def build_release_card() -> InputRichMessage:
    return InputRichMessage(blocks=[
        InputRichBlockSectionHeading(text=f"Релиз {RELEASE}", size=1),
        InputRichBlockParagraph(text=[
            "Тесты зелёные, чейнджлог написан, на часах пятница, 17:45.",
            " Номер релиза можно ",
            RichTextButton(button=RichMessageButton(               # [1]
                text="скопировать одним касанием",
                copy_text=CopyTextButton(text=RELEASE),
            )),
            ", а решение принять кнопками ниже.",
        ]),
        InputRichBlockButtons(                                     # [2]
            buttons=[
                RichMessageButton(
                    text="Катить в прод",
                    style="danger",
                    callback_data="release:deploy",
                ),
                RichMessageButton(
                    text="До понедельника",
                    style="success",
                    callback_data="release:postpone",
                ),
            ],
            align="center",                                        # [3]
        ),
        InputRichBlockButtons(
            buttons=[
                RichMessageButton(
                    text="Чейнджлог",
                    style="primary",
                    url="https://github.com/aiogram/aiogram/releases",
                ),
                RichMessageButton(
                    text="Что вообще происходит?",
                    style="link",                                  # [4]
                    callback_data="release:help",
                ),
                RichMessageButton(
                    text="Откатить",
                    disabled=DisabledButton(),                     # [5]
                ),
            ],
            align="left",
        ),
    ])


@router.message(Command("sendrichbuttons"))
async def cmd_send_rich_buttons(
        message: Message,
) -> None:
    await message.answer_rich(
        rich_message=build_release_card(),
    )


@router.callback_query(F.data.startswith("release:"))              # [6]
async def on_release_button(
        callback: CallbackQuery,
) -> None:
    answers = {
        "release:deploy": "Смелость города берёт. Дежурный предупреждён.",
        "release:postpone": "Мудрое решение. Хороших выходных!",
        "release:help": "Обычный CallbackQuery и обычный F.data, ничего нового.",
    }
    await callback.answer(answers[callback.data], show_alert=True)
```

По пунктам:

1. Кнопка прямо в потоке текста: `RichTextButton` — такой же узел, как `RichTextBold`, и лежит он в общем списке 
   `text` вперемешку со строками. Внутри — обычный `RichMessageButton`, на этот раз с `copy_text`: 
   по нажатию номер релиза уедет в буфер обмена.
2. А это уже блок, отдельный ряд кнопок между абзацем и следующим блоком. Рядов может быть несколько, у нас их два.
3. Выравнивание ряда: верхний ряд по центру, нижний прижат влево. Разрешены `left`, `center` и `right`.
4. Тот самый `style="link"` — кнопка отрисуется простой ссылкой. Напомню, что для кнопок с `url` этот стиль 
   запрещён, только для callback.
5. Кнопка на месте, но нажать её нельзя: `DisabledButton()` — пустой объект вообще без полей. Удобно, когда 
   действие временно недоступно, а выкидывать кнопку из макета не хочется.
6. И самое приятное: нажатие на кнопку внутри Rich Message прилетает **обычным** `CallbackQuery`. Никаких новых 
   типов апдейтов и фильтров учить не надо — привычный `F.data` работает ровно как работал.

Результат:

![Rich Message](images/rich-messages/rich_buttons_dark.png#only-dark){ loading=lazy }
![Rich Message](images/rich-messages/rich_buttons_light.png#only-light){ loading=lazy }

!!! note "`disabled` — не только для Rich Messages"
    В том же обновлении 10.3 поле `disabled` завезли и в обычный `InlineKeyboardButton`. Так что приём 
    «кнопка есть, но неактивна» теперь работает и в привычных инлайн-клавиатурах.

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
   прикрутить любую инлайн-клавиатуру. Появившиеся в 10.3 кнопки [внутри сообщения](#buttons) этот способ 
   не отменяют: клавиатура снизу никуда не делась и по-прежнему удобна, когда кнопка относится ко всему 
   сообщению целиком.
2. Редактирование — через знакомый по обычным сообщениям `edit_text()`. А поскольку мы не передали `reply_markup`,
   после редактирования кнопка исчезнет — все пункты выполнены, нажимать больше нечего.
3. Вместо аргумента `text` передаём `rich_message` с новым содержимым — обычный `InputRichMessage`, 
   точно такой же, как при отправке.

![Rich Message](images/rich-messages/sendrichedit_dark.png#only-dark){ width="500" }
![Rich Message](images/rich-messages/sendrichedit_light.png#only-light){ width="500" }

### Тот же чек-лист на блоках {: id="editing-blocks" }

Присмотритесь к коду выше: `CHECKLIST_BEFORE` и `CHECKLIST_AFTER` — это две почти одинаковые константы, 
отличающиеся только скобками `[ ]`/`[x]` и цифрой прогресса. Пока состояний два, это терпимо, но стоит 
завести третье — и копипаста начнёт расползаться. Вот здесь [блочный режим](#blocks) и выстреливает: 
вместо N констант получается одна функция от состояния.

```python title="bot/handlers/rich_edit_blocks.py"
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputRichBlockList,
    InputRichBlockListItem,
    InputRichBlockParagraph,
    InputRichBlockSectionHeading,
    InputRichMessage,
    Message,
    RichTextBold,
)

router = Router(name="rich_edit_blocks")

TASKS = [
    "Прогнать тесты",
    "Обновить документацию",
    "Задеплоить бота",
]


def build_checklist(done: int) -> InputRichMessage:
    progress = ["Прогресс: ", RichTextBold(text=f"{done} из {len(TASKS)}")]
    if done >= len(TASKS):
        progress.append(" 🎉")

    return InputRichMessage(blocks=[
        InputRichBlockSectionHeading(text="Чек-лист релиза", size=1),
        InputRichBlockParagraph(text=progress),
        InputRichBlockList(items=[
            InputRichBlockListItem(
                # blocks, а не text: пункт списка — это список блоков
                blocks=[InputRichBlockParagraph(text=task)],           # [1]
                has_checkbox=True,                                     # [2]
                is_checked=index < done,
            )
            for index, task in enumerate(TASKS)
        ]),
    ])


def build_keyboard(done: int) -> InlineKeyboardMarkup | None:
    # Все пункты выполнены — кнопка больше не нужна
    if done >= len(TASKS):
        return None
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="Выполнить следующий пункт",
            # Текущий прогресс кладём прямо в callback_data
            callback_data=f"checklist:{done + 1}",                     # [3]
        )
    ]])


@router.message(Command("sendricheditblocks"))
async def cmd_send_rich_edit_blocks(
        message: Message,
) -> None:
    await message.answer_rich(
        rich_message=build_checklist(0),
        reply_markup=build_keyboard(0),
    )


@router.callback_query(F.data.startswith("checklist:"))
async def on_checklist_step(
        callback: CallbackQuery,
) -> None:
    done = int(callback.data.split(":")[1])
    # Перегенерировать сообщение под новое состояние — одна строка
    await callback.message.edit_text(                                  # [4]
        rich_message=build_checklist(done),
        reply_markup=build_keyboard(done),
    )
    await callback.answer()
```

По пунктам:

1. Одни из тех самых граблей: содержимое пункта списка — это `blocks`, список блоков, а не строка. 
   Поэтому каждая задача заворачивается в `InputRichBlockParagraph`.
2. Todo-лист получается за счёт пары `has_checkbox` + `is_checked`. В markdown это были `- [ ]` и `- [x]`.
3. Текущий прогресс храним прямо в `callback_data`, поэтому никакого состояния на стороне бота не нужно.
4. Никакой второй константы: просим `build_checklist()` собрать сообщение для нового значения `done` 
   и отправляем в `edit_text()`. Захотите добавить четвёртую задачу — правите только список `TASKS`.

Визуально результат неотличим от markdown-варианта выше, так что отдельного скриншота он не требует. 
Разница целиком в коде — и она хорошо видна, когда состояний становится больше двух.

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
3. Собственно отправка очередного куска. Обратите внимание, что метод возвращает `True`/`False`, 
а не объект `Message` — это ведь не настоящее сообщение, а превью.
4. Заглушка, которую можно показывать, пока вообще никакого текста нет. Красиво анимировано, кстати. 
Начиная с Bot API 10.2 у тега `<tg-thinking>` есть блок-двойник, так что то же самое можно написать так:

    ```python
    rich_message=InputRichMessage(blocks=[InputRichBlockThinking(text="Думаю...")]),
    ```

    Две детали про эту заглушку, которых легко не заметить в документации. Во-первых, `InputRichBlockThinking` 
    разрешён **только** в `sendRichMessageDraft` — в обычное `sendRichMessage` его положить нельзя, и во входящих 
    сообщениях он не встречается (поэтому в [разделе про парсинг](#parsing) блока такого типа и не будет). 
    Во-вторых, Telegram рекомендует [конкретный набор кастомных эмодзи](https://telegram.dog/addemoji/AIActions) 
    специально для этого блока. Вставить кастомный эмодзи в текст можно через 
    `RichTextCustomEmoji(custom_emoji_id="...", alternative_text="🤔")`, и вот это уже полноценный аргумент 
    за блочный режим в стриминге: в строковой разметке так красиво сделать сложнее.

5. Небольшая пауза между апдейтами, чтобы не упереться в флуд-лимиты. Подбирайте интервал под свою нагрузку.
6. Финал: отправляем полный текст обычным `answer_rich()`. Вот это сообщение уже останется в чате.

!!! note "Не пытайтесь стримить посимвольно"
    Каждый вызов `send_rich_message_draft` — это сетевой запрос. Накопите разумный буфер (несколько слов или строку)
    и отправляйте превью раз в несколько сотен миллисекунд, иначе Telegram быстро прижмёт вас лимитами.

Как это выглядит «в динамике» на видео:

![type:video](images/rich-messages/streaming_dark.mp4)

## Медиафайлы {: id="media" }

Текстом дело не ограничивается — внутрь RM можно встраивать медиа. Самый простой путь — обычная HTTP(S)-ссылка 
прямо в разметке; с него и начнём. А в Bot API 10.2 к нему добавился второй способ, позволяющий приложить 
файл по `file_id` или загрузить его с диска — про него будет [чуть ниже](#media-attach).

В Rich Markdown для медиафайлов поддерживается стандартный Markdown-синтаксис: `![alt-текст](URL "title")`. Однако 
часть с alt-текстом (в обычном вебе он используется в случае, когда медиафайл не загрузился или в режиме «только текст») 
в Telegram нигде не отображается, а видимую подпись нужно задавать сразу после URL в кавычках. 
Впрочем, посмотрите пример ниже и всё поймёте:

```python title="bot/handlers/rich_media.py"
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
    теги: `<img>`, `<video>` и `<audio>` для одиночных медиа, а также кастомные `<tg-collage>` (коллаж) и
    `<tg-slideshow>` (слайд-шоу), внутрь которых вкладываются медиа-блоки. У каждого из этих тегов теперь есть 
    и блок-двойник: `InputRichBlockPhoto`, `InputRichBlockVideo`, `InputRichBlockAudio`, `InputRichBlockCollage`, 
    `InputRichBlockSlideshow` — см. [каталог блоков](#blocks-catalog). Пощупать рендеринг вживую можно в
    [@richtextdemobot](https://telegram.dog/richtextdemobot).

### Свои файлы и `file_id` {: id="media-attach" }

С HTTP-ссылками всё просто, но у них есть очевидное ограничение: файл должен где-то лежать в открытом доступе. 
Отправить картинку, которую бот только что сгенерировал, или переслать медиа по уже известному `file_id` 
таким способом не выйдет. Ровно эту дырку и закрыло поле `media` объекта `InputRichMessage`, появившееся в Bot API 10.2.

Работает оно в паре с разметкой. В тексте (`markdown` или `html`) вы ставите ссылку специального вида — 
`tg://photo?id=<id>`, `tg://video?id=<id>` или `tg://audio?id=<id>`, — а сам файл описываете элементом списка 
`media` с тем же самым `id`:

```python title="bot/handlers/rich_media.py"
CARD_MARKDOWN = """\
# Медиа из своего файла

Картинка ниже уехала в Telegram не по ссылке, а прямо с диска:
в тексте стоит только `tg://photo?id=logo`, а сам файл описан в поле `media`.

![](tg://photo?id=logo "Загружено с диска")
"""


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
```

Внутрь `InputMediaPhoto` (а также `InputMediaVideo`, `InputMediaAudio`, `InputMediaAnimation` 
и `InputMediaVoiceNote`) можно положить всё то же, к чему вы привыкли в обычных методах отправки: `file_id`, 
HTTP-ссылку или локальный файл через `FSInputFile`. В последнем случае aiogram сам соберёт multipart-запрос 
и подставит `attach://`-ссылку — со стороны кода это одна строка, как и всегда.

Отдельно проговорим про `file_id`. Да, работают: в документации 
про ссылки `tg://photo?id=...` прямым текстом написано «to reuse previously uploaded files or upload a new 
file», а описание поля `media` у `InputMediaPhoto` не отличается от того, что вы уже видели в `sendPhoto`. 
Меняется ровно одна строка:

```python title="bot/handlers/rich_media.py"
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
```

Разметка не изменилась вообще: в тексте всё та же ссылка `tg://photo?id=logo`, а способ доставки файла — 
целиком дело поля `media`. Это удобно: можно держать один шаблон сообщения и подставлять в него то файл 
с диска, то `file_id`, то HTTP-ссылку, не трогая сам текст.

!!! warning "Чужой `file_id` не сработает"
    `file_id` привязан к боту, который этот файл загрузил или получил. Если вы запускаете пример со своим
    токеном, константа из книги работать не будет. Возьмите свой: отправьте боту любую картинку и
    распечатайте `message.photo[-1].file_id` — способ ровно тот же, что и в главе
    [про медиафайлы](messages-media.md).


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
        f"Состав:\n{stats}",
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
В этой главе мы научились отправлять такие сообщения всеми тремя способами — `markdown`, `html` и `blocks`, — 
редактировать их, прикладывать к ним свои файлы, разбирать входящие по блокам и стримить ответы через эфемерные 
черновики. Главный практический вывод: разметку удобно писать руками, а блоки — генерировать кодом, и выбирать 
стоит по тому, откуда берётся содержимое сообщения.

За кадром остались отдельные блоки вроде карт и слайд-шоу, но после [каталога блоков](#blocks-catalog) 
они вопросов вызывать уже не должны: принцип везде один и тот же, отличаются только поля. Всё остальное 
вы всегда найдёте в [документации](https://core.telegram.org/bots/api#inputrichmessage) 
и [демо-боте](https://telegram.dog/richtextdemobot).
