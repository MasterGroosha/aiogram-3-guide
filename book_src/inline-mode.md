---
title: 内联模式
description: 内联模式
---

# 内联模式

!!! info ""

    使用的 aiogram 版本： 3.1.1

## 理论 {: id="theory" }

### 为什么需要内联模式？ {: id="why-inline-mode" }

在前几章中，机器人和人类是各自独立交流的，但 Telegram 有一种特殊模式，允许用户在机器人的帮助下以自己的名义发送信息。这就是所谓的**内联模式**，下面是它在现实生活中的样子：

![Пример работы бота @imdb в инлайн-режиме](images/inline_mode/inline_demo.png)

但这样的功能在实践中如何应用呢？我建议大家看看一些近乎官方的 Telegram 机器人名称，它们都有内联模式：

* [@gif](https://t.me/gif) 
* [@wiki](https://t.me/wiki)
* [@imdb](https://t.me/imdb)
* [@youtube](https://t.me/youtube)
* [@foursquare](https://t.me/foursquare)
* [@music](https://t.me/music)
* [@gamee](https://t.me/gamee)
* [@like](https://t.me/like)

这样的例子不胜枚举，但我希望大家都能明白：内联模式非常适合在当前聊天中插入内容。Telegram 将此类机器人的部分功能（如投票、gif）应用到了官方应用中，但其余功能至今仍完全可用。

!!! warning "重要"

    回想一下，如果有一个带有 `callback` 按钮的键盘连接到从内联模式发送的消息上，按下该按钮后，
    机器人将收到一个 `CallbackQuery` 对象，其中没有 `Message` 对象。取而代之的是一个很少使用的 `inline_message_id` 对象。

### 接收请求的格式 {: id="incoming-update-format" }

当用户在聊天中写入机器人用户名并输入文本时，就会创建一个 [InlineQuery](https://core.telegram.org/bots/api#inlinequery) 类型的更新。
如果仔细研究这个对象的字段，你可能会发现一些奇怪的地方。

首先，没有调用机器人的聊天的聊天 ID，取而代之的是一个可选字段 `chat_type` ，显示（如果非空）聊天的类型（私人、群组、超级群组、频道）。
这样做的原因很简单：因为要在内联模式下使用机器人，您不必将其添加到任何东西上，添加一个聊天对象将允许您在购物车中谨慎地跟踪和收集聊天。

其次，有一个字段 `offset` 不是数字，而是字符串。问题是，默认情况下，机器人在响应内联请求时向用户发送的结果不能超过 50 个。
要显示更多结果，必须在响应时传递 `next_offset` 参数，该参数将在下一个 `InlineQuery` 的 `offset` 字段中重复。
因此，机器人会意识到，它需要从 `offset` 开始加载新数据。之所以使用字符串，是因为除了数字外，还可以使用一些标识符，如 `UUID`。

### 发出答复的格式 {: id="outgoing-answer-format" }

回答用户查询的方法只有一种：[answerInlineQuery](https://core.telegram.org/bots/api#answerinlinequery)。
但要发送的类型[多达 20 种](https://core.telegram.org/bots/api#inlinequeryresult)。
更准确地说，实际上有 11 种，因为其余的都是相同的类型，只是输入数据不同，例如，用 `file_id` 代替媒体文件链接。
最好不要把不同的类型混在一起，尤其是不要和其他类型混在一起。让我们分别考虑其中一些类型。

![тип InlineQueryResultArticle](images/inline_mode/inline_articles.jpg)

最常用的类型可能是 [InlineQueryResultArticle](https://core.telegram.org/bots/api#inlinequeryresultarticle)（如上图）。
在所有主要客户端中，它看起来像一叠矩形块，总是有一个标题，有时有一个描述，左边有一个预览图片或只是一个存根。
如果开发人员设置了 `url` 属性，一些客户端就会在描述行下显示指定链接，预览图就会变成可点击的，并直接指向浏览器中的链接本身。
点击字符串会发送 `input_message_content` 参数中指定的内容（该参数为必选参数），这些内容有 5 种不同类型：

* 文本
* 地理位置
* 地标 (venue)
* 联系
* 发票 (invoice)

![тип InlineQueryResultPhoto](images/inline_mode/inline_pictures.png)

其他类型指的是所谓的 "媒体文件"，我们将以图片为例进行说明。
响应一组图像时，数据会以垂直磁贴（如上面的截图）或滚动水平条（如 iOS 版本）的方式排列。

如果再次打开有关 [InlineQueryResult](https://core.telegram.org/bots/api#inlinequeryresult) 的部分，
您会发现照片（与其他类型一样）有两种变体： `InlineQueryResultPhoto` 和 `InlineQueryResultCachedPhoto` 。
不同之处在于，第一个变体接受指向网络图片的链接，而第二个变体接受来自已上传至 Telegram 的媒体的 `file_id` 。

!!! warning "重要"

    在内联模式下，不能直接从文件上传图片。要么是 `URL` ，要么是 `file_id` 。没有第三个选项。

默认情况下，点击结果列表中的媒体文件会将该媒体发送到调用的聊天窗口。
但是，如果您指定了 `input_message_content` 参数（对于媒体文件来说是可选参数），那么点击后将发送该参数中指定的任何内容。
例如，点击一部电影的封面，就会发送电影的文字说明和在线影院的观看链接。
或者，点击员工的照片将以 👀 联系人的形式发送他的电话号码。
顺便说一下，尽管媒体有 `title` 和 `description` 参数，但客户端不会显示它们，而 Bot API 本身也会忽略它们。

answerInlineQuery 方法有几个参数需要我们注意。
首先是 `cache_time` 。它决定了查询结果可以被购物车服务器缓存多长时间，以避免发送给机器人。
如果您的数据是静态的或很少变化，可以随意增加该值。
其次， `is_personal` 标志，它将影响查询结果是只缓存一个用户还是同时缓存所有用户。
如果您的机器人根据用户 ID 显示个性化值，请将其设置为 `True`。

!!! info ""

    这几行的作者有一次忘记在他的机器人 @my_id_bot 中指定 `is_personal` 标志，将缓存设置为 86400 秒（1 天），
    结果听到用户愤愤不平地发送他的 ID 而不是自己的 ID。从别人的错误中学习，而不是从自己的错误中学习。

第三，字符串参数 `next_offset` 可以让您在滚动时加载结果，因为在 `InlineQuery` 的一个响应中返回的值不能超过 50 个。
我们将在另一个示例中考虑 `next_offset` 的使用。

第四， `switch_pm_text` 和 `switch_pm_parameter` 。
除了查询结果外，机器人还可以显示一个小按钮，按钮上方显示参数 `switch_pm_text` 的文本，
点击该按钮类似于 `deeplink`，即用户将进入与机器人的私人对话，按钮上显示的不是输入框，
而是一个 "`开始`" 按钮，点击后机器人将收到一条文本为 `/start ТЕКСТ` 的消息，其中的文本不是 `TEXT`，而是参数 `switch_pm_parameter` 的值。

![Кнопка switch_pm](images/inline_mode/switch_pm_button.png)

如果某个查询没有结果，或者您想让用户有机会快速添加内容，使用该功能非常方便。还有一个功能，我们将在稍后的机器人开发过程中考虑。说到它...

## 实践 {: id="practice" }

要让机器人知道在内联模式下调用时要显示什么，它需要一些数据：事先存储的数据或从用户处接收的数据。举个例子，让我们编写一个机器人，它将从用户那里接收链接和图片，然后根据请求在内联模式下显示所有这些内容。

!!! info ""

    别忘了通过 [@BotFather](https://t.me/botfather) 启用机器人的内联模式：
    Bot Settings -> Inline Mode -> Turn on

### 存储系统 {: id="storage" }

由于本章已经很长了，为了避免过多涉及细节，我们同意测试机器人将使用普通的内存字典作为模拟数据库。这样就不用担心在调试过程中重置状态的问题，同时也简化了事先填充存储空间的过程，如果你突然想用现成的链接或图片运行机器人的话。两种数据类型各有三个函数：添加数据、获取数据、删除数据。以下是该文件的全部代码：

```python title="storage.py"
from typing import Optional

# В реальной жизни здесь должна быть нормальная СУБД.
# Но для примера нам будет достаточно показать на обычном словаре.
# Учтите, что он сбрасывается при перезапуске бота.
data = dict()


def add_link(
        telegram_id: int,
        link: str,
        title: str,
        description: Optional[str]
):
    """
    Сохраняет ссылку в словарь

    :param telegram_id: ID юзера в Telegram
    :param link: текст ссылки
    :param title: заголовок ссылки
    :param description: (опционально) описание ссылки
    """
    data.setdefault(telegram_id, dict())
    data[telegram_id].setdefault("links", dict())
    data[telegram_id]["links"][link] = {
        "title": title,
        "description": description
    }

def add_photo(
        telegram_id: int,
        photo_file_id: str,
        photo_unique_id: str
):
    """
    Сохраняет изображение в словарь

    :param telegram_id: ID юзера в Telegram
    :param photo_file_id: file_id изображения
    :param photo_unique_id: file_unique_id изображения
    """
    data.setdefault(telegram_id, dict())
    data[telegram_id].setdefault("images", [])
    if photo_file_id not in data[telegram_id]["images"]:
        data[telegram_id]["images"].append((photo_file_id, photo_unique_id))

def get_links_by_id(telegram_id: int) -> dict:
    """
    Получает сохранённые ссылки пользователя

    :param telegram_id: ID юзера в Telegram
    :return: если по юзеру есть данные, то словарь со ссылками
    """
    if telegram_id in data and "links" in data[telegram_id]:
        return data[telegram_id]["links"]
    return dict()

def get_images_by_id(telegram_id: int) -> list[str]:
    """
    Получает сохранённые изображения пользователя

    :param telegram_id: ID юзера в Telegram
    :return:
    """
    if telegram_id in data and "images" in data[telegram_id]:
        return [item[0] for item in data[telegram_id]["images"]]
    return []

def delete_link(telegram_id: int, link: str):
    """
    Удаляет ссылку

    :param telegram_id: ID юзера в Telegram
    :param link: ссылка
    """
    if telegram_id in data:
        if "links" in data[telegram_id]:
            if link in data[telegram_id]["links"]:
                del data[telegram_id]["links"][link]

def delete_image(telegram_id: int, photo_file_unique_id: str):
    """
    Удаляет изображение

    :param telegram_id: ID юзера в Telegram
    :param photo_file_unique_id: file_unique_id изображения для удаления
    """
    if telegram_id in data and "images" in data[telegram_id]:
        for index, (_, unique_id) in enumerate(data[telegram_id]["images"]):
            if unique_id == photo_file_unique_id:
                data[telegram_id]["images"].pop(index)
```

### 机器人中的命令 {: id="common-commands" }

机器人有几条常用命令： `/start` 、 `/help` 、 `/save` 、 `/delete` 和 `/cancel` 。
前两个是信息性的， `/save` 启动保存数据的进程， `/delete` 启动删除数据的进程， `/cancel` 分别中断一个正在运行的进程。
让我们从 `/save` 命令开始。

### 保存数据 {: id="data-saving" }

这一次，我们将在一个单独的文件中描述状态，以便于导入。
为此，我们将创建一个文件 `states.py` 并实现一个类 `SaveCommon` ，其中将有一个状态 "`等待输入`"：

```python title="states.py"
from aiogram.fsm.state import StatesGroup, State

class SaveCommon(StatesGroup):
    waiting_for_save_start = State()
```

现在，让我们来处理不同类型信息的保存问题

#### 保存文本 {: id="save-text" }

让我们从文本信息开始。想法很简单：用户发送一条信息。如果至少有一个链接，就会提取出来，然后提示用户输入链接名称（必填）和描述。最后一步可以用 `/skip` 跳过。如果有多个链接，则只提取第一个链接。

除了上述的 "`等待输入`" 状态外，还将有两个特定于文本的状态："`等待标题输入`" 和 "`等待描述输入`"。在 `states.py` 中，我们将添加这些状态：

```python title="states.py"
# тут предыдущий код

class TextSave(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
```

让我们从 `SaveCommon` -> `waiting_for_save_start` 状态下的每个文本的两个处理程序开始。
我们需要捕捉带有链接的信息。在有关 [过滤器和中间件](filters-and-middlewares.md#filters-as-classes) 的章节中，我们已经做了一个类似的过滤器，但针对的是用户名。
现在，我们要复制该过滤器，并将其用于链接：

```python title="filters/text_has_link.py"
from typing import Union, Dict, Any

from aiogram.filters import BaseFilter
from aiogram.types import Message


class HasLinkFilter(BaseFilter):
    async def __call__(self, message: Message) -> Union[bool, Dict[str, Any]]:
        # Если entities вообще нет, вернётся None,
        # в этом случае считаем, что это пустой список
        entities = message.entities or []

        # Если есть хотя бы одна ссылка, возвращаем её
        for entity in entities:
            if entity.type == "url":
                return {"link": entity.extract_from(message.text)}

        # Если ничего не нашли, возвращаем None
        return False
```

为了缩短导入时间，让我们编辑文件 `filters/__init__.py` ：

```python title="filters/__init__.py"
from .text_has_link import HasLinkFilter

# Делаем так, чтобы затем просто импортировать
# from filters import HasLinkFilter
__all__ = [
    "HasLinkFilter"
]
```

为什么每个文本需要两个处理程序？第一个处理程序将捕捉有链接的信息，第二个处理程序将捕捉没有链接的信息。写作：

```python title="handlers/save_text.py"
# <импорты>

@router.message(SaveCommon.waiting_for_save_start, F.text, HasLinkFilter())
async def save_text_has_link(message: Message, link: str, state: FSMContext):
    await state.update_data(link=link)
    await state.set_state(TextSave.waiting_for_title)
    await message.answer(
        text=f"Окей, я нашёл в сообщении ссылку {link}. "
             f"Теперь отправь мне заголовок (не больше 30 символов)"
    )

@router.message(SaveCommon.waiting_for_save_start, F.text)
async def save_text_no_link(message: Message):
    await message.answer(
        text="Эмм.. я не нашёл в твоём сообщении ссылку. "
             "Попробуй ещё раз или нажми /cancel, чтобы отменить."
    )
```

接下来，希望用户输入记录标题。在这里，我们也可以将逻辑分成两个处理程序：成功和不幸情况下的巧合：

```python title="handlers/save_text.py" hl_lines="3"
# импорты и предыдущие шаги

@router.message(TextSave.waiting_for_title, F.text.func(len) <= 30)
async def title_entered_ok(message: Message, state: FSMContext):
    await state.update_data(title=message.text, description=None)
    await state.set_state(TextSave.waiting_for_description)
    await message.answer(
        text="Так, заголовок вижу. Теперь введи описание "
             "(тоже не больше 30 символов) "
             "или нажми /skip, чтобы пропустить этот шаг"
    )

@router.message(TextSave.waiting_for_title, F.text)
async def too_long_title(message: Message):
    await message.answer("Слишком длинный заголовок. Попробуй ещё раз")
    return
```

请注意代码 `F.text.func(len) <= 30` 。
魔术过滤器允许您向输入传递一些函数，这些函数将在 `.func` 之前指定的任何内容上执行。
例如， `F.text.func(len) -> len(F.text)` ，并且只有当 `.text` 属性不是 `None` 时才会执行（换句话说，这里还有一个内容提示检查）。
但总的来说，在 [magic-filter](https://github.com/aiogram/magic-filter/blob/3c5e38fd5cd359fd961e26bab17e65201b02c1c6/magic_filter/magic.py#L227-L228) 中支持 `len() ： F.text.len() <= 30` 。

接下来是描述的处理程序。在这里，我们可以再次将其分为两个处理程序....。等等，但是 `too_long_title()` 函数也可以用于描述步骤，因为我们有相同的文本限制！让我们重新命名它，并在另一个步骤中添加一个过滤器：

```python title="handlers/save_text.py"
@router.message(TextSave.waiting_for_title, F.text)
@router.message(TextSave.waiting_for_description, F.text)
async def text_too_long(message: Message):  # бывш. too_long_title()
    await message.answer("Слишком длинный заголовок. Попробуй ещё раз")
    return
```

现在让我们来看看最后一个处理程序，我们可以通过输入简短描述或 `/skip` 命令来处理它。因为我们需要捕捉两个输入，所以要挂起两个装饰器，在参数中接受可选的 `CommandObject` 并查看内部：如果没有命令，那么我们就输入了一个描述：

```python title="handlers/save_text.py"
# Эта функция должна быть ПЕРЕД text_too_long() !
@router.message(TextSave.waiting_for_description, F.text.func(len) <= 30)
@router.message(TextSave.waiting_for_description, Command("skip"))
async def last_step(
        message: Message,
        state: FSMContext,
        command: Optional[CommandObject] = None
):
    if not command:
        await state.update_data(description=message.text)
    # Сохраняем данные в нашу ненастоящую БД
    data = await state.get_data()
    add_link(message.from_user.id, data["link"], data["title"], data["description"])

    await message.answer("Ссылка сохранена!")
    await state.clear()
```

因此，我们制作了一组处理程序，用于保存对内存数据库的引用。下面是整个文件的代码：

```python title="handlers/save_text.py"
from typing import Optional

from aiogram import Router, F
from aiogram.filters.command import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from filters import HasLinkFilter
from states import SaveCommon, TextSave
from storage import add_link

router = Router()

@router.message(SaveCommon.waiting_for_save_start, F.text, HasLinkFilter())
async def save_text_has_link(message: Message, link: str, state: FSMContext):
    await state.update_data(link=link)
    await state.set_state(TextSave.waiting_for_title)
    await message.answer(
        text=f"Окей, я нашёл в сообщении ссылку {link}. "
             f"Теперь отправь мне описание (не больше 30 символов)"
    )

@router.message(SaveCommon.waiting_for_save_start, F.text)
async def save_text_no_link(message: Message):
    await message.answer(
        text="Эмм.. я не нашёл в твоём сообщении ссылку. "
             "Попробуй ещё раз или нажми /cancel, чтобы отменить."
    )

@router.message(TextSave.waiting_for_title, F.text.func(len) <= 30)
async def title_entered_ok(message: Message, state: FSMContext):
    await state.update_data(title=message.text, description=None)
    await state.set_state(TextSave.waiting_for_description)
    await message.answer(
        text="Так, заголовок вижу. Теперь введи описание "
             "(тоже не больше 30 символов) "
             "или нажми /skip, чтобы пропустить этот шаг"
    )

@router.message(TextSave.waiting_for_description, F.text.func(len) <= 30)
@router.message(TextSave.waiting_for_description, Command("skip"))
async def last_step(
        message: Message,
        state: FSMContext,
        command: Optional[CommandObject] = None
):
    if not command:
        await state.update_data(description=message.text)
    # Сохраняем данные в нашу ненастоящую БД
    data = await state.get_data()
    add_link(message.from_user.id, data["link"], data["title"], data["description"])
    await state.clear()
    kb = [[InlineKeyboardButton(
        text="Попробовать",
        switch_inline_query="links"
    )]]
    await message.answer(
        text="Ссылка сохранена!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )

@router.message(TextSave.waiting_for_title, F.text)
@router.message(TextSave.waiting_for_description, F.text)
async def text_too_long(message: Message):
    await message.answer("Слишком длинный заголовок. Попробуй ещё раз")
    return
```

#### 保存图片 {: id="save-images" }

图片就简单多了；只需一步即可添加。但有一个细微差别：除了用于稍后显示的 `file_id` 外，
我们还需要保存 `file_unique_id` ，因为当我们允许用户删除已保存的图片时，它就会派上用场：

```python title="handlers/save_images.py"
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, PhotoSize
from states import SaveCommon
from storage import add_photo

router = Router()

@router.message(SaveCommon.waiting_for_save_start, F.photo[-1].as_("photo"))
async def save_image(message: Message, photo: PhotoSize, state: FSMContext):
    add_photo(message.from_user.id, photo.file_id, photo.file_unique_id)
    await message.answer("Изображение сохранено!")
    await state.clear()
```

### 显示数据 {: id="show-data" }

好了，我们已经学会了如何保存数据，现在需要以某种方式显示数据。
为此，机器人应捕捉 `inline_query` 类型的更新，处理程序将接收 [InlineQuery](https://core.telegram.org/bots/api#inlinequery) 类型的对象。
我们不会在空查询中显示任何内容（暂时），我们将在 `@bot links` 查询中显示链接列表，在 `@bot images` 查询中显示图片。
当然， `@bot` 将显示机器人的用户名。

#### 显示文本 {: id="show-text" }

要响应文本信息，我们需要收集一个对象列表，其类型为 [InlineQueryResultArticle](https://core.telegram.org/bots/api#inlinequeryresultarticle) 。我们已经拥有了所有必要的（甚至是额外的）数据：

![Содержимое объекта InlineQueryResultArticle](images/inline_mode/article_content.png "Содержимое объекта InlineQueryResultArticle")

对于 `input_message_content` 参数，让我们编写一个简单的嵌套函数，根据有无描述返回文本：

```python
def get_message_text(
        link: str,
        title: str,
        description: Optional[str]
) -> str:
    text_parts = [f'{html.bold(html.quote(title))}']
    if description:
        text_parts.append(html.quote(description))
    text_parts.append("")  # добавим пустую строку
    text_parts.append(link)
    return "\n".join(text_parts)
```

现在让我们来描述一下处理程序本身：

```python title="handlers/inline_mode.py"
@router.inline_query(F.query == "links")
async def show_user_links(inline_query: InlineQuery):

    # Эта функция просто собирает текст, который будет
    # отправлен при нажатии на вариант в инлайн-режиме
    def get_message_text():
        # эта вложенная функция описана выше ↑

    results = []
    for link, link_data in get_links_by_id(inline_query.from_user.id).items():
        # В итоговый массив запихиваем каждую запись
        results.append(InlineQueryResultArticle(
            id=link,  # ссылки у нас уникальные, потому проблем не будет
            title=link_data["title"],
            description=link_data["description"],
            input_message_content=InputTextMessageContent(
                message_text=get_message_text(
                    link=link,
                    title=link_data["title"],
                    description=link_data["description"]
                ),
                parse_mode="HTML"
            )
        ))
    # Важно указать is_personal=True!
    await inline_query.answer(results, is_personal=True)
```

最后，我们得到了（第二张唱片缺少了金库的一个步骤 `description` ）：

![Просмотр ссылок](images/inline_mode/our_links_result.png "Просмотр ссылок")

当你点击它时，就会收到这样一条漂亮的信息：

![Результат в чате](images/inline_mode/our_links_result_in_chat.png "Результат в чате")

#### 显示图片 {: id="show-images" }

对于图像来说，这一点比较简单，但这里有一个细微差别：我们不能使用图像的 `file_id` 作为特定变体的 id，因为它的长度超过了 64 字节（Bot API 限制）。因此，我们将使用转换为字符串的数组中元素的序列号。除此之外，代码与之前的非常相似：

```python title="handlers/inline_mode.py"
@router.inline_query(F.query == "images")
async def show_user_images(inline_query: InlineQuery):
    results = []
    for index, file_id in enumerate(get_images_by_id(inline_query.from_user.id)):
        # В итоговый массив запихиваем каждую запись
        results.append(InlineQueryResultCachedPhoto(
            id=str(index),  # индекс элемента в list
            photo_file_id=file_id
        ))
    # Важно указать is_personal=True!
    await inline_query.answer(results, is_personal=True)
```

结果呢？

![Отображение картинок в инлайн-режиме](images/inline_mode/our_images_result.png "Отображение картинок в инлайн-режиме")

### 删除数据 {: id="delete-data" }

保存的内容需要不时清理。因此，我们希望允许用户删除累积的链接和/或图片。为此，我们将为 `/delete` 命令创建一个处理程序。
但我们不想强迫用户输入机器人用户名并写入 `links` 或 `images` 。为此，我们将在命令响应下放置两个按钮。
一个将打开内联模式，用于查看链接，另一个用于查看图片。

在 `states.py` 中添加一个新类：

```python title="states.py"
class DeleteCommon(StatesGroup):
    waiting_for_delete_start = State()
```

现在，让我们为 `/delete` 命令创建一个处理程序：

```python title="handlers/common.py" hl_lines="7 13"
# новый импорт
from aiogram.filters.state import StateFilter

@router.message(Command("delete"), StateFilter(None))
async def cmd_delete(message: Message, state: FSMContext):
    kb = []
    kb.append([
        InlineKeyboardButton(
            text="Выбрать ссылку",
            switch_inline_query_current_chat="links"
        )
    ])
    kb.append([
        InlineKeyboardButton(
            text="Выбрать изображение",
            switch_inline_query_current_chat="images"
        )
    ])
    await state.set_state(DeleteCommon.waiting_for_delete_start)
    await message.answer(
        text="Выберите, что хотите удалить:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )
```

点击这样一个按钮，就会将所需的值替换为内联模式，从而立即打开一个链接或图片列表（为了演示起见，我暂时去掉了弹出菜单，以便按钮可见）：

![Кнопка switch_inline_query_current_chat](images/inline_mode/cmd_delete.png "Кнопка switch_inline_query_current_chat")

如果我们只使用 `switch_inline_query` 而不是 `switch_inline_query_current_chat` ，Telegram 就会提供选择一个用户可以写信的聊天室，然后在那里替换指定的文本。

剩下的工作就是编写一个路由器，用来捕捉删除请求并编辑版本库的内容：

```python title="handlers/delete_data.py"
# импорты
router = Router()

@router.message(
    DeleteCommon.waiting_for_delete_start,
    F.text,
    ViaBotFilter(),
    HasLinkFilter()
)
async def link_deletion_handler(message: Message, link: str, state: FSMContext):
    delete_link(message.from_user.id, link)
    await state.clear()
    await message.answer(
        text="Ссылка удалена! "
             "Выдача инлайн-режима обновится в течение нескольких минут.")

@router.message(
    DeleteCommon.waiting_for_delete_start,
    F.photo[-1].file_unique_id.as_("file_unique_id"),
    ViaBotFilter()
)
async def image_deletion_handler(
        message: Message,
        state: FSMContext,
        file_unique_id: str
):
    delete_image(message.from_user.id, file_unique_id)
    await state.clear()
    await message.answer(
        text="Изображение удалено! "
             "Выдача инлайн-режима обновится в течение нескольких минут.")
```

请注意：我们通过 `file_unique_id` 删除图像，因为每次发送图像时， `file_id` 都会不同（简而言之：完整的 `file_id` 包含时间戳和其他非永久性数据）。


### Switch 的参数 {: id="switch-parameter" }

在前面讨论[发送回复的格式](#outgoing-answer-format)时，我们看到了以 `switch_pm` 为前缀的参数。
让我们使用它们，这样用户就可以直接从任何聊天中添加数据，而不仅仅是从与机器人的聊天中添加数据。

让我们将上述参数添加到内联请求处理程序中。为此，让我们重写 `handlers/inline_mode.py` 文件中的 `answer_inline_query()` 方法调用：

```python
await inline_query.answer(
        results, is_personal=True,
        switch_pm_text="Добавить ещё »»",
        switch_pm_parameter="add"
    )
```

在 `/save` 命令的 `handlers/common.py` 处理程序文件中，让我们使用 `add` deeplink 通过 `CommandStart` 过滤器添加另一个入口点：

```python title="handlers/common.py" hl_lines="4"
# новый импорт:
from aiogram.filters.command import CommandStart

@router.message(CommandStart(magic=F.args == "add"))
@router.message(Command("save"), StateFilter(None))
async def cmd_save(message: Message, state: FSMContext):
    ...

# Учтите, что хэндлер на просто /start должен идти ПОЗЖЕ
@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    ...
```

此外，在添加文字和图片的最后一步，让我们添加一个 `switch_inline_query` 按钮，并建议尝试在另一个聊天工具中添加内容：

```python
# файл handlers/save_text.py
@router.message(TextSave.waiting_for_description, F.text.func(len) <= 30)
@router.message(TextSave.waiting_for_description, Command("skip"))
async def last_step(...):
    # тут остальной код функции
    kb = [[InlineKeyboardButton(
        text="Попробовать",
        switch_inline_query="links"
    )]]
    await message.answer(
        text="Ссылка сохранена!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )

# файл handlers/save_images.py
@router.message(SaveCommon.waiting_for_save_start, F.photo[-1].as_("photo"))
async def save_image(...):
    # тут остальной код функции
    kb = [[InlineKeyboardButton(
        text="Попробовать",
        switch_inline_query="images"
    )]]
    await message.answer(
        text="Изображение сохранено!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )
```

内联模式的另一个很酷的功能是：如果你呼叫一个不在 PM 中的机器人，转到 "`添加更多`" 按钮，并到达最后一步，那么当机器人用 `switch_inline_query` - 按钮发送消息时，Telegram 客户端会自动将用户返回到原始聊天，并立即用所需文本打开内联模式！


## 补充说明 {: id="extras" }

### 加载结果 {: id="lazy-loading" }

根据机器人 API 文档，您最多可以在一次 [answerInlineQuery](https://core.telegram.org/bots/api#answerinlinequery) 调用中发送 50 个项目。
如果需要更多呢？在这种情况下， `next_offset` 参数就派上用场了。
该参数由机器人自己指定，当用户滚动浏览当前堆栈时，下一个内联查询中也会出现相同的值。
例如，让我们编写一个简单的数字生成器，返回每包 50 个项目，但最大值为 195 的数字：

```python title="handlers/inline_pagination_demo.py"
def get_fake_results(start_num: int, size: int = 50) -> list[int]:
    """
    Генерирует список из последовательных чисел

    :param start_num: стартовое число для генератора
    :param size: размер пачки (по умолч. 50)
    :return: список последовательных чисел
    """
    overall_items = 195
    # Если результатов больше нет, отправляем пустой список
    if start_num >= overall_items:
        return []
    # Отправка неполной пачки (последней)
    elif start_num + size >= overall_items:
        return list(range(start_num, overall_items+1))
    else:
        return list(range(start_num, start_num+size))
```

现在，让我们编写一个内联处理程序，这样当我们接近当前列表的末尾时，Telegram 就会请求继续。

为此，我们要检查开头的 `offset` 字段，如果为空，则将其设置为 1。接下来，我们生成一个假的结果列表。
如果输出正好包含 50 个对象，我们就会在响应中指定 `next_offset` 等于当前值 + 50。
如果对象数量较少，我们就不指定任何内容，这样 Telegram 就不会再次尝试加载新字符串：

```python title="handlers/inline_pagination_demo.py" hl_lines="21"
@router.inline_query(F.query == "long")
async def pagination_demo(
        inline_query: InlineQuery,
):
    # Высчитываем offset как число
    offset = int(inline_query.offset) if inline_query.offset else 1
    results = [InlineQueryResultArticle(
        id=str(item_num),
        title=f"Объект №{item_num}",
        input_message_content=InputTextMessageContent(
            message_text=f"Объект №{item_num}"
        )
    ) for item_num in get_fake_results(offset)]
    if len(results) < 50:
        await inline_query.answer(
            results, is_personal=True
        )
    else:
        await inline_query.answer(
            results, is_personal=True, 
            next_offset=str(offset+50)
        )
```

当机器人滚动浏览内联结果时，它将接收查询并返回越来越多的结果，直到到达第 195 个元素时，查询才会停止。

### 内联反馈 {: id="inline-feedback" }

虽然知道的人不多，但 Telegram 允许您在内联模式下收集有关机器人使用情况的简单统计数据。
要开始使用，您需要为 @BotFather 启用相应的设置： `/mybots -（选择机器人） - 机器人设置 - 内联反馈`：

![Пример работы бота @imdb в инлайн-режиме](images/inline_mode/botfather_inline_feedback.png "Пример работы бота @imdb в инлайн-режиме")

按钮上的数字表示用户在内联模式下选择对象时收到 [ChosenInlineResult](https://core.telegram.org/bots/api#choseninlineresult) 事件的概率。例如，如果值设置为 10%，那么每次选择对象时，机器人就有 10% 的概率收到 ChosenInlineResult 事件。Telegram 不建议将值设为 100%，因为这会加倍机器人的负载。因此，该功能并不适合用于任何严肃的分析，但如果技术娴熟，经过长时间使用，它可以提供最有用的内联结果的大致信息。此类事件的处理程序示例：

```python title="handlers/inline_chosen_result_demo.py"
from aiogram import Router
from aiogram.types import ChosenInlineResult

router = Router()

@router.chosen_inline_result()
async def pagination_demo(
        chosen_result: ChosenInlineResult,
):
    # Пишем прямо на экран. Но, возможно, вы захотите сохранять куда-то
    print(
        f"After '{chosen_result.query}' query, "
        f"user chose option with ID '{chosen_result.result_id}'"
    )
```

尽管 Telegram 不建议为 "`内联反馈`" 设置较大的值，但它至少有一个实际用途：有些音乐机器人会尝试按需下载歌曲的完整版本，而不事先保存歌曲。如果在内联模式下调用机器人，可能无法在 10-15 秒内完成下载，之后机器人 API 会返回一个关于 "`过期`" 更新的错误。

开发人员是这样做的：当机器人搜索曲目时，会在预览中提供一个简短的样本（5-10 秒）。
当用户点击某一行时，系统会发送一条音频信息，并附带一个内嵌按钮（否则无法编辑信息），
机器人会捕捉到发送事件，从 `ChosenInlineResult` 类型的更新中提取信息的 `inline_message_id` 端到端 `inline_message_id` ，
加载完整版本的音频，并使用该 `inline_message_id` 将样本编辑成完整的曲目。没错，Telegram 已经开始习惯使用拐杖了。
