---
title: Текстовые сообщения
description: Работа с текстовыми сообщениями
---

# Текстовые сообщения

!!! info ""
    Используемая версия aiogram: 3.30.0

В этой главе мы разберёмся, как отправлять и принимать различные текстовые сообщения и
как использовать различные типы форматирования.

Приём и отправка текстовых сообщений — это одно из важнейших действий у большинства ботов. Почти любое начало диалога 
с ботом выполняется командой `/start` и практически всегда бот в ответ присылает какой-то текст. С давних пор в Telegram 
всем доступны различные способы форматирования сообщений: выделение жирным шрифтом, курсив, подчёркивание, зачёркивание, 
создание ссылок и многое другое. Со стороны ботов эти и другие «украшательства» представлены аж в четырёх вариантах: 
HTML, Markdown, MarkdownV2 и Rich Messages. Но говорить далее будем не обо всех них, поскольку обычный Markdown 
без цифры 2 считается устаревшим и здесь рассматриваться не будет, 
а про Rich Messages подробно рассказано в [отдельной главе](rich-messages.md).

## Приём текстовых сообщений

В прошлой главе вы уже видели простейший пример хэндлера на входящее сообщение любого типа:

```python
@dp.message()
async def any_message(
        message: Message,
):
    await message.answer("Hello world!")
```

Чтобы принимать именно текстовые сообщения, надо добавить фильтр «принимать только текст». 
Самый простой способ для этого – указать магический фильтр `F.text`:

```python
@dp.message(F.text)
async def any_text_message(
        message: Message,
):
    await message.answer("Вижу твоё текстовое сообщение")
```

Про «магический фильтр» **F** мы поговорим в [другой главе](filters-and-middlewares.md), но сейчас надо просто запомнить, 
что конструкция `@dp.message(F.text)` означает «хэндлер на объект типа `Message`, у которого значение атрибута `text` не равно None».
Иными словами – ловим сообщения с каким-то текстом. В следующем примере на входящее 
сообщение с текстом «Дата» бот будет отвечать сегодняшней датой, а на текст «Время», соответственно, временем. И для этого 
в фильтре надо будет сравнить значение атрибута `text` с желаемым. Смотрим:

```python
from datetime import datetime

from aiogram import F, Router
from aiogram.types import Message

router = Router(name="date_and_time")


@router.message(F.text == "Дата")
async def current_date(
        message: Message,
) -> None:
    await message.answer(
        f"У бота сегодня {datetime.now().strftime("%d.%m.%Y")}"
    )


@router.message(F.text == "Время")
async def current_time(
        message: Message,
) -> None:
    await message.answer(
        f"У бота сейчас на часах {datetime.now().strftime("%H:%M")}"
    )
```

![Реакция бота на тексты 'Дата' и 'Время'](images/messages_text/date_and_time_dark.png#only-dark)
![Реакция бота на тексты 'Дата' и 'Время'](images/messages_text/date_and_time_light.png#only-light)

А что, если мы хотим пощадить пользователей ПК и избавить их от необходимости каждый раз зажимать Shift, 
набирая «Дата» с большой буквы? Иными словами, хэндлер должен реагировать одинаково на два разных текста. Делать два 
отдельных хэндлера с одинаковым кодом внутри **плохо**, поскольку это нарушает 
[принцип DRY](https://ru.wikipedia.org/wiki/Don’t_repeat_yourself). Но в aiogram можно навесить несколько фильтров-декораторов на одну 
функцию и это будет считаться логическим **ИЛИ**: 

```python
@router.message(F.text == "Дата")
@router.message(F.text == "дата")
async def current_date(
        message: Message,
) -> None:
    await message.answer(
        f"У бота сегодня {datetime.now().strftime("%d.%m.%Y")}"
    )
```

??? "Альтернативный вариант"
    Куда же без регулярных выражений! Два декоратора выше можно заменить на один:
    ```python
    @router.message(F.text.regexp(r"(?i)^дата$"))
    async def current_date(
            message: Message,
    ) -> None:
        await message.answer(
            f"У бота сегодня {datetime.now().strftime("%d.%m.%Y")}"
        )
    ```
    Такой вариант полностью регистронезависимый и будет срабатывать даже на «ДАТА»

Чтобы получить логическое **И**, достаточно перечислить фильтры внутри декоратора через запятую. Например, 
следующая конструкция означает «текстовое сообщение И айди чата 123456»:

```python
@router.message(F.text, F.chat.id == 123456)
```

## Команды

Вместо того чтобы реагировать на какой-то конкретный текст на конкретном языке, да ещё и полагаясь на то, что данный 
текст будет отправлен именно как триггер для бота, ботам доступна такая вещь, как команды. Команда — это текст в формате 
`/command`, где в начале обязательно слэш, а затем до 32 символов латинского алфавита, цифры или подчёркивания. 

Командами могут быть:

* `/start`  
* `/set_timer`  
* `/01_continue`  

Следующие тексты не являются командами:

* `/привет` (кириллические символы не допускаются)
* `/!корова%` (символы ! и % не допускаются, кириллица тоже) 
* `\something` (слэш не в ту сторону)

Когда пользователь впервые начинает диалог с ботом внизу экрана появляется кнопка «Начать», при нажатии на которую 
от лица пользователя боту отправляется команда `/start`. Следовательно, очень важно всегда иметь обработчик на эту 
команду, а что в нём делать — на ваше усмотрение: приветствие, справка или что-то ещё. 

??? warning "`/start` может не всегда быть первой командой!"
    Многие разработчики справедливо считают, что с команды `/start` всегда начинается взаимодействие пользователя и бота 
    и поэтом на неё обработчик можно вешать логику регистрации пользователя, создание записей в базе данных и т.д. 
    Однако есть, как минимум, одна ситуация, при котором начало диалога будет отличаться.  
    Воспроизвести очень просто: добавьте в описание бота (его bio) какую-либо команду. И тогда при нажатии на эту команду 
    первым сообщением будет именно она, а не `/start`. Учтите это при оформлении профиля бота и написании логики.
    
Напишем очень простой хэндлер на команду `/start` с приветствием пользователя. Для команд в aiogram существует специальный 
фильтр `Command`:

```python
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="basic_commands")


@router.message(Command("start"))
async def cmd_start(
        message: Message,
) -> None:
    await message.answer(
        "Привет и добро пожаловать!"
    )
```

## Команды с аргументами

При проектировании команд может возникнуть ситуация, когда сама по себе команда не даёт нужной универсальности. 
Простой пример: вы делаете команду `/set_timer` для отложенной отправки сообщений и хотите, чтобы можно было указать 
время. Разумеется, делать разные команды `/set_timer_1m`, `/set_timer_2m`, `/set_timer_3m` бесполезно и глупо, это лишь 
усложнит разработку. 

В такой ситуации есть два грамотных подхода: через FSM (конечные автоматы, о них в [отдельной главе](fsm.md)) или 
через параметризацию команд. В таком случае будет ожидаться не просто `/set_timer`, а `/set_timer <время> <текст>`. 
Реализуем второй способ по следующим правилам:

* Если вызывают команду без аргументов (`/set_timer`), то ругаемся на их отсутствие.
* Если передан только один аргумент, то ругаемся и показываем правильный формат.
* Если передано больше двух аргументов, то второй и последующий трактуем как один большой текст.
* В конце пишем, что таймер добавлен, логику самого таймера здесь не реализуем и формат времени (`10m`, `3h`, `20d` и т.д.) тоже не проверяем.

Для работы с параметрами есть специальный объект `CommandObject`, который автоматически заполнится 
aiogram-ом, если используется фильтр для команд и если в параметры хэндлера добавить параметр 
`command`, как на примере кода ниже:

```python
from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

router = Router(name="commands_args")


@router.message(Command("set_timer"))
async def cmd_set_timer(
        message: Message,
        command: CommandObject
) -> None:
    # Если не переданы никакие аргументы, то
    # command.args будет None
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return
    # Пробуем разделить аргументы на две части по первому встречному пробелу
    try:
        delay_time, text_to_send = command.args.split(" ", maxsplit=1)
    # Если получилось меньше двух частей, вылетит ValueError
    except ValueError:
        await message.answer(
            "Ошибка: неправильный формат команды.\n"
            "Правильный формат: /set_timer ВРЕМЯ ТЕКСТ\n"
            "Например: /set_timer 5m таймер на пять минут"
        )
        return
    await message.answer(
        "Таймер добавлен!\n"
        f"Время: {delay_time}\n"
        f"Текст: {text_to_send}"
    )
```

Результат:

![Парсинг аргументов команд](images/messages_text/command_args_dark.png#only-dark)
![Парсинг аргументов команд](images/messages_text/command_args_light.png#only-light)


## Префикс команд

С командами может возникнуть небольшая проблема в группах: Telegram автоматически подсвечивает команды, начинающиеся 
со слэша, из-за чего порой случается вот такое (спасибо дорогим участником 
[моей группы](https://telegram.dog/+DE0_2nCvbXozZjUy) за помощь в создании скриншота):

![Флуд командами](images/messages_text/commands_spam_dark.png#only-dark)
![Флуд командами](images/messages_text/commands_spam_light.png#only-light)

Чтобы этого избежать, можно заставить бота реагировать на команды с другими префиксами. Они не будут подсвечиваться, 
их нельзя будет поместить в меню команд, также они потребуют полностью ручной ввод, 
так что сами оценивайте пользу такого подхода:

```python
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="commands_prefixes")


@router.message(Command("custom1", prefix="%"))
async def cmd_custom1(message: Message) -> None:
    await message.answer("Вижу команду!")


# Можно указать несколько префиксов........vv...
@router.message(Command("custom2", prefix="/!"))
async def cmd_custom2(message: Message) -> None:
    await message.answer("И эту тоже вижу!")
```

![Различные префиксы команд](images/messages_text/custom_prefixes_dark.png#only-dark)
![Различные префиксы команд](images/messages_text/custom_prefixes_light.png#only-light)


Обратите внимание: из-за того, что кастомные префиксы делают команды командами только с точки зрения aiogram 
(на стороне Telegram это всё ещё обычный текст), то возникает проблема с использованием таких команд в группах, 
т.к. боты не-админы со включенным Privacy Mode (по умолчанию) могут 
не увидеть такие команды из-за [особенностей](https://core.telegram.org/bots/faq#what-messages-will-my-bot-get) 
логики Телеграма. Из-за этого кастомные префиксы лучше всего использовать вместе с ботами-модераторам групп, 
которые уже являются администраторами, либо в личных сообщениях.

## Диплинки {: id="deeplinks" }

Команда `/start` умеет то, чего не умеют остальные: принимать параметр прямо из ссылки. 
Если сформировать ссылку вида `t.me/bot?start=xxx`, то при переходе по ней бот получит 
сообщение `/start xxx`, а пользователю ничего вводить не придётся. Такая ссылка называется 
**диплинком** и годится для кучи вещей: шорткаты к командам, реферальные ссылки, привязка 
аккаунта на вашем сайте к Telegram и т.д.

!!! info "Ограничения на payload"
    В параметр можно засунуть только символы `A-Z`, `a-z`, `0-9`, `_` и `-`, суммарно 
    не более 64 символов. Всё остальное (пробелы, кириллица, JSON) нужно предварительно 
    закодировать — Telegram рекомендует base64url, и в aiogram для этого есть готовые функции 
    (см. ниже).

### Обработка диплинков

В aiogram есть специальный фильтр `CommandStart` непосредственно для `/start`. Необязательно использовать его, чтобы 
ловить `/start` без параметров, однако для работы диплинков он необходим. Также при работе с диплинками в такой фильтр 
требуется передать специальный параметр: `CommandStart(deep_link=True)`.


```python
import re

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message

router = Router(name="deeplinks")


@router.message(Command("help"))
@router.message(CommandStart(
    deep_link=True, magic=F.args == "help"
))
async def cmd_help(message: Message):
    await message.answer(
        "Это сообщение показывается как на команду /help, "
        "так и по диплинку t.me/bot?start=help"
    )


@router.message(CommandStart(
    deep_link=True,
    magic=F.args.regexp(re.compile(r"secretfile_(?P<file_id>\d{1,6})"))
))
async def start_secret_file_deeplink(
        message: Message,
        command: CommandObject
):
    file_id = command.magic_result["file_id"]
    await message.answer(f"Отправляю секретный документ №{file_id}")
```

![type:video](images/messages_text/deeplinks_demo.mp4)


### Генерация ссылок

Собирать ссылку руками не обязательно, в aiogram есть 
[набор функций](https://docs.aiogram.dev/en/latest/utils/deep_linking.html):

```python
from aiogram.utils.deep_linking import create_start_link

link = await create_start_link(bot, "secretfile_42")
# https://t.me/bot?start=secretfile_42
```

Если нужно передать что-то, что не влезает в разрешённый набор символов, добавьте 
`encode=True` и тогда payload будет превращён в base64-формат. На стороне хэндлера тогда достаточно 
указать флаг `deep_link_encoded=True`, и в `command.args` приедет уже раскодированная 
строка:

```python
@router.message(CommandStart(deep_link=True, deep_link_encoded=True))
async def start_encoded_deeplink(
        message: Message,
        command: CommandObject
):
    await message.answer(f"Payload: {command.args}")
```

### Не только личка

Помимо `start` есть ещё два типа ссылок:

* `t.me/bot?startgroup=xxx` — предложит выбрать группу и добавить бота туда. 
  После добавления в группу отправится сообщение `/start@your_bot xxx`. Функция-хелпер: 
  `create_startgroup_link()`.
* `t.me/bot?startapp=xxx` — откроет Mini App бота и передаст параметр туда. 
  Функция-хелпер: `create_startapp_link()`.

!!! danger "Payload — это ввод от пользователя"
    Ссылку никто не проверяет: любой может просто взять и отправить боту 
    `/start secretfile_9999` или `/start ref_1` руками, не переходя ни по какой ссылке. 
    Поэтому payload нельзя считать доверенным. Обязательно валидируйте его на своей 
    стороне и не кладите в него ничего, что само по себе даёт права. Если делаете 
    реферальную систему — проверяйте, что приглашающий и приглашённый это разные люди, 
    и что приглашённый действительно новый. Для некоторых вариантов использование UUID в качестве 
    параметра start-ссылки будет хорошей практикой.

!!! tip "Больше диплинков, но не для ботов"
    В документации Telegram есть подробное описание всевозможных диплинков для клиентских 
    приложений: [https://core.telegram.org/api/links](https://core.telegram.org/api/links)

## Форматированный вывод {: id="formatting-options" }

За выбор форматирования при отправке сообщений отвечает аргумент `parse_mode`, например:
```python
from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode

# Если не указать фильтр F.text, 
# то хэндлер сработает даже на картинку с подписью /test
@dp.message(F.text, Command("test"))
async def any_message(message: Message):
    await message.answer(
        "Hello, <b>world</b>!", 
        parse_mode=ParseMode.HTML
    )
    await message.answer(
        "Hello, *world*\!", 
        parse_mode=ParseMode.MARKDOWN_V2
    )
```

![Hello world с разным форматированием](images/messages/l02_1.png)

Если в боте повсеместно используется определённое форматирование, то каждый раз указывать аргумент `parse_mode` довольно 
накладно. К счастью, в aiogram можно задать параметры бота по умолчанию. Для этого создайте объект `DefaultBotProperties` 
и передайте туда нужные настройки:

```python
from aiogram.client.default import DefaultBotProperties

bot = Bot(
    token="123:abcxyz",
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
        # тут ещё много других интересных настроек
    )
)

# где-то в функции...
await message.answer("Сообщение с <u>HTML-разметкой</u>")
# чтобы явно отключить форматирование в конкретном запросе, 
# передайте parse_mode=None
await message.answer(
    "Сообщение без <s>какой-либо разметки</s>", 
    parse_mode=None
)
```

![Настройка типа разметки по умолчанию](images/messages/l02_2.png)

## Экранирование ввода {: id="input-escaping" }

Нередко бывают ситуации, когда окончательный текст сообщения бота заранее неизвестен 
и формируется исходя из каких-то внешних данных: имя пользователя, его ввод и т.д. 
Напишем хэндлер на команду `/hello`, который будет приветствовать пользователя по его полному имени
(`first_name + last_name`), например: «Hello, Иван Иванов»:

```python
from aiogram.filters import Command

@dp.message(Command("hello"))
async def cmd_hello(message: Message):
    await message.answer(
        f"Hello, <b>{message.from_user.full_name}</b>",
        parse_mode=ParseMode.HTML
    )
```

И вроде всё хорошо, бот приветствует пользователей:

![Работа команды /hello](images/messages/cmd_hello_before.png)

Но тут приходит юзер с именем &lt;Славик777&gt; и бот молчит! А в логах видно следующее:
`aiogram.exceptions.TelegramBadRequest: Telegram server says - Bad Request: can't parse entities: 
Unsupported start tag "Славик777" at byte offset 7`

Упс, у нас стоит режим форматирования HTML, и Telegram пытается распарсить &lt;Славик777&gt; как HTML-тег. Непорядок. 
Но у этой проблемы есть несколько решений. Первое: экранировать передаваемые значения.

```python
from aiogram import html
from aiogram.filters import Command

@dp.message(Command("hello"))
async def cmd_hello(message: Message):
    await message.answer(
        f"Hello, {html.bold(html.quote(message.from_user.full_name))}",
        parse_mode=ParseMode.HTML
    )
```

Второе чуть сложнее, но более продвинутое: воспользоваться специальным инструментом, который будет 
собирать отдельно текст и отдельно информацию о том, какие его куски должны быть отформатированы.

```python
from aiogram.filters import Command
from aiogram.utils.formatting import Text, Bold

@dp.message(Command("hello"))
async def cmd_hello(message: Message):
    content = Text(
        "Hello, ",
        Bold(message.from_user.full_name)
    )
    await message.answer(
        **content.as_kwargs()
    )
```

В примере выше конструкция `**content.as_kwargs()` вернёт аргументы `text`, `entities`, `parse_mode` и 
подставит их в вызов `answer()`.

![Работа команды /hello после фиксов](images/messages/cmd_hello_after.png)

Упомянутый инструмент форматирования довольно комплексный, 
[официальная документация](https://docs.aiogram.dev/en/latest/utils/formatting.html) демонстрирует удобное отображение 
сложных конструкций, например:

```python
from aiogram.filters import Command
from aiogram.utils.formatting import (
    Bold, as_list, as_marked_section, as_key_value, HashTag
)

@dp.message(Command("advanced_example"))
async def cmd_advanced_example(message: Message):
    content = as_list(
        as_marked_section(
            Bold("Success:"),
            "Test 1",
            "Test 3",
            "Test 4",
            marker="✅ ",
        ),
        as_marked_section(
            Bold("Failed:"),
            "Test 2",
            marker="❌ ",
        ),
        as_marked_section(
            Bold("Summary:"),
            as_key_value("Total", 4),
            as_key_value("Success", 3),
            as_key_value("Failed", 1),
            marker="  ",
        ),
        HashTag("#test"),
        sep="\n\n",
    )
    await message.answer(**content.as_kwargs())
```

![Продвинутый пример](images/messages/advanced_example.png)

!!! info ""
    Подробнее о различных способах форматирования и поддерживаемых тегах можно узнать 
    [в документации Bot API](https://core.telegram.org/bots/api#formatting-options).

## Сохранение форматирования {: id="keep-formatting" }

Представим, что бот должен получить форматированный текст от пользователя и добавить туда что-то 
своё, например, отметку времени. Напишем простой код:

```python
# новый импорт!
from datetime import datetime

@dp.message(F.text)
async def echo_with_time(message: Message):
    # Получаем текущее время в часовом поясе ПК
    time_now = datetime.now().strftime('%H:%M')
    # Создаём подчёркнутый текст
    added_text = html.underline(f"Создано в {time_now}")
    # Отправляем новое сообщение с добавленным текстом
    await message.answer(f"{message.text}\n\n{added_text}", parse_mode="HTML")
```

![Добавленный текст (неудачная попытка)](images/messages/keep_formatting_bad.png)

Мда, что-то пошло не так, почему сбилось форматирование исходного сообщения? 
Это происходит из-за того, что `message.text` возвращает просто текст, без каких-либо оформлений. 
Чтобы получить текст в нужном форматировании, воспользуемся альтернативными свойствами: 
`message.html_text` или `message.md_text`. Сейчас нам нужен первый вариант. Заменяем в примере 
выше `message.text` на `message.html_text` и получаем корректный результат:

![Добавленный текст (успех)](images/messages/keep_formatting_good.png)

## Работа с entities {: id="message-entities" }

Telegram сильно упрощает жизнь разработчикам, выполняя предобработку сообщений пользователей на своей стороне. 
Например, некоторые сущности, типа e-mail, номера телефона, юзернейма и др. можно не доставать 
[регулярными выражениями](https://ru.wikipedia.org/wiki/Регулярные_выражения), а извлечь 
напрямую из объекта [Message](https://core.telegram.org/bots/api#message) и поля 
`entities`, содержащего массив объектов типа 
[MessageEntity](https://core.telegram.org/bots/api#messageentity). В качестве примера напишем 
хэндлер, который извлекает ссылку, e-mail и моноширинный текст из сообщения (по одной штуке).  
Здесь кроется важный подвох. **Telegram возвращает не сами значения, а их начало в тексте и длину**. 
Более того, текст считается в символах UTF-8, а entities работают с UTF-16, из-за этого, если просто взять 
позицию и длину, то при наличии UTF-16 символов (например, эмодзи) ваш обработанный текст просто съедет. 

Лучше всего это демонстрирует пример ниже. На скриншоте первый ответ бота есть результат парсинга «в лоб», 
а второй — результат применения аиограмного метода `extract_from()` над entity. На вход ему передаётся весь исходный текст:

```python
@dp.message(F.text)
async def extract_data(message: Message):
    data = {
        "url": "<N/A>",
        "email": "<N/A>",
        "code": "<N/A>"
    }
    entities = message.entities or []
    for item in entities:
        if item.type in data.keys():
            # Неправильно
            # data[item.type] = message.text[item.offset : item.offset+item.length]
            # Правильно
            data[item.type] = item.extract_from(message.text)
    await message.reply(
        "Вот что я нашёл:\n"
        f"URL: {html.quote(data['url'])}\n"
        f"E-mail: {html.quote(data['email'])}\n"
        f"Пароль: {html.quote(data['code'])}"
    )
```

![Парсинг entities](images/messages/parse_entities.png)


## Предпросмотр ссылок {: id="link-previews" }

Обычно при отправке текстового сообщения со ссылками Telegram пытается найти и показать предпросмотр первой по порядку ссылки. 
Это поведение можно настроить по своему желанию, передав в качестве аргумента `link_preview_options` метода `send_message()` 
объект `LinkPreviewOptions`:

```python
# Новый импорт
from aiogram.types import LinkPreviewOptions

@dp.message(Command("links"))
async def cmd_links(message: Message):
    links_text = (
        "https://nplus1.ru/news/2024/05/23/voyager-1-science-data"
        "\n"
        "https://telegram.dog/telegram"
    )
    # Ссылка отключена
    options_1 = LinkPreviewOptions(is_disabled=True)
    await message.answer(
        f"Нет превью ссылок\n{links_text}",
        link_preview_options=options_1
    )

    # -------------------- #

    # Маленькое превью
    # Для использования prefer_small_media обязательно указывать ещё и url
    options_2 = LinkPreviewOptions(
        url="https://nplus1.ru/news/2024/05/23/voyager-1-science-data",
        prefer_small_media=True
    )
    await message.answer(
        f"Маленькое превью\n{links_text}",
        link_preview_options=options_2
    )

    # -------------------- #

    # Большое превью
    # Для использования prefer_large_media обязательно указывать ещё и url
    options_3 = LinkPreviewOptions(
        url="https://nplus1.ru/news/2024/05/23/voyager-1-science-data",
        prefer_large_media=True
    )
    await message.answer(
        f"Большое превью\n{links_text}",
        link_preview_options=options_3
    )

    # -------------------- #

    # Можно сочетать: маленькое превью и расположение над текстом
    options_4 = LinkPreviewOptions(
        url="https://nplus1.ru/news/2024/05/23/voyager-1-science-data",
        prefer_small_media=True,
        show_above_text=True
    )
    await message.answer(
        f"Маленькое превью над текстом\n{links_text}",
        link_preview_options=options_4
    )

    # -------------------- #

    # Можно выбрать, какая ссылка будет использоваться для предпосмотра,
    options_5 = LinkPreviewOptions(
        url="https://telegram.dog/telegram"
    )
    await message.answer(
        f"Предпросмотр не первой ссылки\n{links_text}",
        link_preview_options=options_5
    )
```

Результат: 
![Примеры предпросмотров ссылок](images/messages/link_preview_options.png)

Также некоторые параметры предпросмотра можно указать по умолчанию в `DefaultBotProperties`, о чём рассказывалось 
в начале главы.

## Бонус: прячем ссылку в тексте {: id="bonus" }

Бывают ситуации, когда хочется отправить длинное сообщение с картинкой, но лимит на подписи к медиафайлам составляет 
всего 1024 символа против 4096 у обычного текстового, а вставлять внизу ссылку на медиа — выглядит некрасиво.  
Для решения этой проблемы ещё много лет назад придумали подход со «скрытыми ссылками» в HTML-разметке. Суть в том, что 
можно поместить ссылку в [пробел нулевой ширины](http://www.fileformat.info/info/unicode/char/200b/index.htm) и вставить 
всю эту конструкцию в начало сообщения. Для наблюдателя в сообщении нет ничего лишнего, а сервер Telegram всё видит и честно 
добавляет предпросмотр.  
Разработчики aiogram для этого даже сделали специальный вспомогательный метод `hide_link()`:
```python
# новый импорт!
from aiogram.utils.markdown import hide_link

@dp.message(Command("hidden_link"))
async def cmd_hidden_link(message: Message):
    await message.answer(
        f"{hide_link('https://telegra.ph/file/562a512448876923e28c3.png')}"
        f"Документация Telegram: *существует*\n"
        f"Пользователи: *не читают документацию*\n"
        f"Груша:"
    )
```

![Изображение со скрытой ссылкой](images/messages/hidden_link.png)

А при помощи LinkPreviewOptions (см. выше) можно сделать медиафайл сверху с длинной подписью в 4096 символов ниже, что 
пригодится в [следующей главе](messages-media.md) при работе с медиафайлами.

На этом всё. До следующих глав!  
<s><small>Ставьте лайки, подписывайтесь, прожимайте колокольчик</small></s>
