---
title: 处理信息
description: 处理信息
---

# 处理信息

!!! info ""
    使用的 aiogram 版本： 3.1.1

本章将向您介绍如何对信息应用不同类型的格式，以及如何处理媒体文件。

## 文本 {: id="text" }
处理文本信息可能是大多数机器人最重要的操作之一。您几乎可以用文本表达任何内容，而且您希望以一种 _漂亮_ 的方式呈现信息。开发人员可以使用三种文本标记方法：HTML、Markdown 和 MarkdownV2。HTML 和 MarkdownV2 被认为是其中最先进的，而 «经典» Markdown 支持的功能较少，在 aiogram 中已不再使用。

在了解 aiogram 中处理文本的方法之前，有必要提及 aiogram 3.x 与 2.x 之间的一个重要区别："2 "版本默认只处理文本信息，而 "3 "版本则处理任何类型的信息。更准确地说，您现在应该只接受文本信息：

```python
# 使用装饰器
@dp.message_handler()
async def func_name(...)

# 使用注册函数
dp.register_message_handler(func_name)

# 使用装饰器（魔法过滤）
from aiogram import F
@dp.message(F.text)
async def func_name(...)

# 使用注册函数（魔法过滤）
dp.message.register(func_name, F.text)
```
我们将在下一章讨论 **F** 的 [魔法过滤](filters-and-middlewares.md)。

### 格式化输出 {: id="formatting-options" }

例如， `parse_mode` 参数负责在发送信息时选择格式：
```python
from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode

# 如果不指定过滤器 F.text, 
# 这样，即使是在标题为 /test 的图片上，处理程序也能正常工作。
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

如果一个机器人在任何地方都使用某种格式，那么每次都指定 `parse_mode` 参数就会非常麻烦。幸运的是，在 aiogram 中，你可以直接向 **Bot** 对象传递所需的类型，如果在特定情况下需要不使用格式化，只需指定 `parse_mode=None` 即可：


```python
bot = Bot(token="123:abcxyz", parse_mode="HTML")

# 函数中的某处...
await message.answer("消息来自 <u>HTML-标记</u>")
await message.answer(
    "消息没有 <s>任何标记</s>", 
    parse_mode=None
)
```

![Настройка типа разметки по умолчанию](images/messages/l02_2.png)

### 转义输入 {: id="input-escaping" }

在很多情况下，机器人消息的最终文本并不是事先就知道的，而是根据一些外部数据形成的：用户名、用户输入等。例如，让我们为 `/hello` 命令编写一个处理程序，用用户的全名（ `first_name` + `last_name` ）向用户问好：例如：«你好，伊万»：

```python
from aiogram.filters import Command

@dp.message(Command("hello"))
async def cmd_hello(message: Message):
    await message.answer(
        f"Hello, <b>{message.from_user.full_name}</b>",
        parse_mode=ParseMode.HTML
    )
```

一切似乎都很顺利，机器人欢迎用户的到来：

![Работа команды /hello](images/messages/cmd_hello_before.png)

但是来了一个名为 &lt;Car777&gt; 的用户，而机器人却保持沉默！日志显示如下
`aiogram.exceptions.TelegramBadRequest: Telegram server says - Bad Request: can't parse entities: 
Unsupported start tag "Car777" at byte offset 7`

哎呀，我们使用的是 HTML 格式化模式，Telegram 正试图将 &lt;Car777&gt; 解析为 HTML 标记。这可不好。但有几种方法可以解决这个问题。第一种是屏蔽传递的值。

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

第二种方法稍微复杂一些，但也更先进：使用一种特殊的工具，分别收集文本和其中哪些部分应该格式化的信息。

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

在上面的示例中， `**content.as_kwargs()` 结构体将返回参数 `text` , `entities` , `parse_mode` 并将它们代入 `answer()` 调用中。

![Работа команды /hello после фиксов](images/messages/cmd_hello_after.png)

上述[格式化工具](https://docs.aiogram.dev/en/latest/utils/formatting.html)相当全面，例如，官方文档演示了如何方便地显示复杂的设计：

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
    您可以在 [Bot API 文档](https://core.telegram.org/bots/api#formatting-options)中进一步了解不同的格式化方法和支持的标记。

### 保存格式化 {: id="keep-formatting" }

假设一个机器人需要接收来自用户的格式化文本，并在其中添加自己的内容，例如时间戳。让我们编写一段简单的代码：

```python
# 导入
from datetime import datetime

@dp.message(F.text)
async def echo_with_time(message: Message):
    # 获取 PC 时区的当前时间
    time_now = datetime.now().strftime('%H:%M')
    # 创建下划线文本
    added_text = html.underline(f"Создано в {time_now}")
    # 发送带有新增文本的新信息
    await message.answer(f"{message.text}\n\n{added_text}", parse_mode="HTML")
```

![Добавленный текст (неудачная попытка)](images/messages/keep_formatting_bad.png)

是的，出错了，为什么原始信息的格式会一团糟？这是因为 `message.text` 返回的只是文本，没有任何格式。要获得正确格式的文本，我们可以使用其他属性： `message.html_text` 或 `message.md_text` 。现在我们需要第一个选项。我们将上例中的 `message.text` 替换为 `message.html_text` 即可得到正确的结果：

![Добавленный текст (успех)](images/messages/keep_formatting_good.png)

### 与实体合作 {: id="message-entities" }

Telegram 通过预处理用户消息大大简化了开发人员的工作。
例如，某些实体（如电子邮件、电话号码、用户名等）可以直接从[消息](https://core.telegram.org/bots/api#message)对象和包含 [MessageEntity](https://core.telegram.org/bots/api#messageentity) 对象数组的 entities 字段中提取，而无需使用[正则表达式](https://en.wikipedia.org/wiki/Regular_expression)。
例如，让我们编写一个处理程序，从消息中提取链接、电子邮件和单行文字（各一个）。

这里有一个重要的问题。**Telegram 返回的不是值本身，而是它们在文本中的起始位置和长度。**
此外，文本是以 UTF-8 字符计算的，而实体是以 UTF-16 工作的，因此如果只计算位置和长度，那么如果有 UTF-16 字符（例如表情符号），处理过的文本就会被移走。

下面的示例最能说明这一点。在截图中，机器人的第一个响应是解析 `head-on`的结果，第二个响应是对实体应用 aiogram 方法 `extract_from()` 的结果。
整个源文本作为输入传递给了机器人：

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
            # 不正确
            # data[item.type] = message.text[item.offset : item.offset+item.length]
            # 正确的
            data[item.type] = item.extract_from(message.text)
    await message.reply(
        "Вот 我发现了什么:\n"
        f"URL: {html.quote(data['url'])}\n"
        f"E-mail: {html.quote(data['email'])}\n"
        f"Пароль: {html.quote(data['code'])}"
    )
```

![Парсинг entities](images/messages/parse_entities.png)

### 命令及其参数 {: id="commands-args" }

Telegram 为用户提供了[多种输入信息](https://core.telegram.org/bots/features#inputs)的方式。
其中之一就是命令：以斜线开头的关键字，如 `/new` 或 `/ban` 。
有时，机器人会在命令本身后加上一些参数，如 `/ban 2d` 或 `/settimer 20h This is delayed message` 。作为 aiogram 的一部分，有一个过滤器 `Command()` 可以简化开发人员的工作。
让我们在代码中实现最后一个例子：

```python
@dp.message(Command("settimer"))
async def cmd_settimer(
        message: Message,
        command: CommandObject
):
    # 如果没有传递参数，则
    # command.args 为 None
    if command.args is None:
        await message.answer(
            "错误：未传递参数"
        )
        return
    # 我们尝试通过第一个空格将参数分成两部分
    try:
        delay_time, text_to_send = command.args.split(" ", maxsplit=1)
    # 如果少于两个部分，将产生 ValueError 错误
    except ValueError:
        await message.answer(
            "错误：命令格式不正确。示例:\n"
            "/settimer <time> <message>"
        )
        return
    await message.answer(
        "添加计时器!\n"
        f"时间: {delay_time}\n"
        f"文本: {text_to_send}"
    )
```

让我们尝试用不同的参数（或完全不带参数）传递命令，并检查响应：

![Аргументы команд](images/messages/command_args.png)

群组中的命令可能存在一个小问题：Telegram 会自动高亮以斜线开头的命令，这有时会导致这种情况发生：

![Флуд командами](images/messages/commands_flood.png)

为了避免这种情况，您可以让机器人响应带有其他前缀的命令。这些命令不会突出显示，需要完全手动输入，因此请自行判断这种方法是否有用。

```python
@dp.message(Command("custom1", prefix="%"))
async def cmd_custom1(message: Message):
    await message.answer("let me see!")


# Можно указать несколько префиксов....vv...
@dp.message(Command("custom2", prefix="/!"))
async def cmd_custom2(message: Message):
    await message.answer("yes,i too!")
```

![Кастомные префиксы](images/messages/command_custom_prefix.png)

在群组中使用自定义前缀的唯一问题是，由于服务器逻辑的原因，已启用[隐私模式](https://core.telegram.org/bots/faq#what-messages-will-my-bot-get)（默认）的非管理员机器人可能看不到此类命令。
最常见的使用情况是已经是管理员的群组版主机器人。

### 深层链接 {: id="deeplinks" }

在 Telegram 中，有一个团队可以提供更多的服务。它就是 `/start` 。
关键在于，它可以形成一个类似 `t.me/bot?start=xxx` 的链接，点击该链接后，用户将看到 `开始` 按钮，点击该按钮后，机器人将收到 `/start xxx` 消息。
也就是说，链接中嵌入了一些无需手动输入的附加参数。这就是所谓的 deeplink（不要与 dickpick 混淆），可用于多种不同用途：激活不同命令的快捷方式、推荐系统、快速机器人配置等。
让我们写两个例子：

```python
import re
from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject, CommandStart

@dp.message(Command("help"))
@dp.message(CommandStart(
    deep_link=True, magic=F.args == "help"
))
async def cmd_start_help(message: Message):
    await message.answer("这是一条帮助消息")


@dp.message(CommandStart(
    deep_link=True,
    magic=F.args.regexp(re.compile(r'book_(\d+)'))
))
async def cmd_start_book(
        message: Message,
        command: CommandObject
):
    book_number = command.args.split("_")[1]
    await message.answer(f"Sending book №{book_number}")
```

![Примеры диплинков](images/messages/deeplinks.png)

请注意，通过 `start` 发送的链接会将用户发送到私人机器人。
要选择一个群组并向其发送 deeplink，请将 `start` 替换为 `startgroup` 。
此外，aiogram 还有一个方便的功能，可以直接从[代码](https://github.com/aiogram/aiogram/blob/228a86afdc3c594dd9db9e82d8d6d445adb5ede1/aiogram/utils/deep_linking.py#L126-L158)中创建 deeplink。

!!! tip "更多深层链接，但不针对机器人"
    Telegram 文档详细介绍了客户端应用程序的各种 [https://core.telegram.org/api/links](https://core.telegram.org/api/links)


## 媒体文件 {: id="media" }

### 发送文件 {: id="uploading-media" }

除了常规文本消息外，Telegram 还允许您共享各种类型的媒体文件：照片、视频、gif、地理位置、贴纸等。大多数媒体文件都有 `file_id` 和 `file_unique_id` 属性。
第一种属性可用于多次重发同一文件，而且发送将是即时的，因为文件本身已在 Telegram 服务器上。这是最可取的方法。

例如，下面的代码将使机器人立即以发送的相同 gif 回复用户：

```python
@dp.message(F.animation)
async def echo_gif(message: Message):
    await message.reply_animation(message.animation.file_id)
```

!!! warning "始终使用正确的 file_id！"
    机器人只能使用它**直接**收到的 `file_id` ，例如在用户的私人消息中或在群组/频道中看到媒体文件后收到的file_id。
    如果您尝试使用来自其他机器人的 `file_id` ，它可能会起作用，但过一段时间后，您就会收到指定 **错误 url/file_id** 的错误信息。
    因此，只能使用自己的 `file_id` ！

与 `file_id` 不同的是， `file_unique_id` 标识不能用于重新发送或下载媒体文件，但对特定媒体的所有机器人来说都是一样的。
当多个机器人需要知道各自的 `file_id` 指向同一个文件时，通常需要使用 `file_unique_id` 。

如果 Telegram 服务器上还不存在文件，机器人可以通过三种不同方式上传文件：

 - 作为文件系统中的文件
 - 通过链接上传
 - 直接作为一组字节上传

为了加快发送速度并更小心地使用 Telegram 服务器，最好先上传一次 Telegram 文件，然后使用 `file_id` ，第一次媒体上传后就可以使用。

在 aiogram 3.x 中，有 3 个用于发送文件和媒体的类 - `FSInputFile` , `BufferedInputFile` , `URLInputFile` , 它们可以在[文档](https://docs.aiogram.dev/en/dev-3.x/api/upload_file.html)中找到。

让我们来看一个以各种不同方式发送图像的简单例子：
```python
from aiogram.types import FSInputFile, URLInputFile, BufferedInputFile

@dp.message(Command('images'))
async def upload_photo(message: Message):
    # 我们将在此处输入已发送文件的 file_id，以便稍后使用它们
    file_ids = []

    # 为了演示 BufferedInputFile，让我们使用一个 "经典 "文件
    # 用`open()`打开文件。但是，一般来说，这种方法
    # 最适合从 RAM 发送字节
    # 在进行任何操作（例如通过 Pillow 编辑）后
    with open("buffer_emulation.jpg", "rb") as image_from_buffer:
        result = await message.answer_photo(
            BufferedInputFile(
                image_from_buffer.read(),
                filename="image from buffer.jpg"
            ),
            caption="图片来自缓冲区"
        )
        file_ids.append(result.photo[-1].file_id)

    # 从系统中发送文件
    image_from_pc = FSInputFile("image_from_pc.jpg")
    result = await message.answer_photo(
        image_from_pc,
        caption="电脑文件中的图像"
    )
    file_ids.append(result.photo[-1].file_id)

    # 通过链接发送文件
    image_from_url = URLInputFile("https://picsum.photos/seed/groosha/400/300")
    result = await message.answer_photo(
        image_from_url,
        caption="通过链接查看图片"
    )
    file_ids.append(result.photo[-1].file_id)
    await message.answer("发送文件:\n"+"\n".join(file_ids))
```

### 下载文件 {: id="downloading-media" }

除了重复用于发送外，机器人还可以将媒体下载到自己的计算机/服务器上。
为此， `Bot` 类型的对象有一个 `download()` 方法。在下面的示例中，文件被直接下载到文件系统中，
但没有人阻止你将文件保存到内存中的 BytesIO 对象中，以便传递给下一步的应用程序（如 pillow）。

```python
@dp.message(F.photo)
async def download_photo(message: Message, bot: Bot):
    await bot.download(
        message.photo[-1],
        destination=f"/tmp/{message.photo[-1].file_id}.jpg"
    )


@dp.message(F.sticker)
async def download_sticker(message: Message, bot: Bot):
    await bot.download(
        message.sticker,
        # 对于 Windows，需要更正路径
        destination=f"/tmp/{message.sticker.file_id}.webp"
    )
```

对于图像，我们使用 `message.photo[-1]` 而不是 `message.photo` ，为什么？
因为信息中的 Telegram 照片会同时有几份；它们是尺寸不同的同一张图片。
因此，如果我们使用最后一个元素（索引-1），我们就可以使用可用照片的最大尺寸。

!!! info "下载大文件"

    使用 Telegram Bot API 的机器人可以[下载]((https://core.telegram.org/bots/api#getfile))最大 20 兆字节的文件。
    如果您计划下载/上传大文件，应考虑使用与 Telegram 客户端 API 交互的库，
    而不是 Telegram Bot API，如 [Telethon](https://docs.telethon.dev/en/latest/index.html)  或 [Pyrogram](https://docs.pyrogram.org/)。

    很多人都不知道，客户端 API 不仅可以被普通账户使用，也可以被[机器人使用](https://docs.telethon.dev/en/latest/concepts/botapi-vs-mtproto.html)。

    从 Bot API 5.0 版开始，您可以使用[自建Bot API](https://core.telegram.org/bots/api#using-a-local-bot-api-server)服务器处理大型文件。


### 媒体组 {: id="albums" }

我们在 Telegram 中所说的 "相册"（媒体组）实际上是单个媒体信息，它们共享一个共同的 `media_group_id` 并在客户端上可视化地 `组合` 在一起。

从 3.1 版开始，aiogram 就有了[媒体组生成器](https://docs.aiogram.dev/en/latest/utils/media_group.html)，我们现在要考虑的就是如何使用它。
不过，首先值得一提的是媒体组的一些特性：

* 你不能给它们安装内嵌键盘，也不能用它们发送重放键盘。没办法。绝对不行
* 相册中的每个媒体文件都可以有自己的标题。如果只有一个媒体有标题，它将作为整个相册的共同标题显示。
* 照片可以与同一相册中的视频混合发送，文件（文档）和音乐（音频）不能与任何内容混合发送，只能与同类型的媒体混合发送。
* 一个相册最多可包含十 (10) 个媒体文件。

现在，让我们看看如何在 aiogram 中实现这一点：

```python
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message
from aiogram.utils.media_group import MediaGroupBuilder

@dp.message(Command("album"))
async def cmd_album(message: Message):
    album_builder = MediaGroupBuilder(
        caption="即将发行的媒体组的一般标题"
    )
    album_builder.add(
        type="photo",
        media=FSInputFile("image_from_pc.jpg")
        # caption="特定媒体标题"

    )
    # 如果我们马上就知道了类型，那么就不需要通用的添加
    # 可以立即调用 add_<type>
    album_builder.add_photo(
        # 对于链接或 file_id，只需立即指定其值即可
        media="https://picsum.photos/seed/groosha/400/300"
    )
    album_builder.add_photo(
        media="<ваш file_id>"
    )
    await message.answer_media_group(
        # 不要忘记调用 build()
        media=album_builder.build()
    )
```

结果: 

![Результат работы билдера](images/messages/media_group_builder.png)

但下载相册的情况要糟糕得多....。
如上所述，相册只是一组单独的信息，这意味着它们会以不同的更新方式到达机器人。
几乎没有一种 100% 可靠的方法能一次性接收整张专辑，但你可以尝试将损失降到最低。
这通常是通过 midlvari 实现的，我自己实现的接受媒体组的方法可在[此链接](https://github.com/MasterGroosha/telegram-feedback-bot-topics/blob/master/bot/middlewares/albums_collector.py)中找到。

## 服务消息 {: id="service" }

Telegram 中的信息分为文本信息、媒体文件和服务信息。现在我们来谈谈后者。

![Сервисные сообщения](images/messages/service_messages.png)

尽管它们看起来很不寻常，与它们的交互也很有限，但它们仍然是有自己图标甚至所有者的信息。
值得注意的是，服务信息的使用范围在过去几年中发生了变化，现在您的机器人可能无法使用它们，或者只会删除它们。

我们先不谈细节，只看一个具体的例子：向已登录的会员发送欢迎消息。
这种服务消息的 `content_type` 将等于 `new_chat_members`，但一般来说，它是一个填写了相同字段的消息对象。

```python
@dp.message(F.new_chat_members)
async def somebody_added(message: Message):
    for user in message.new_chat_members:
        # 属性 full_name 同时采用名字和姓氏
        # (在上面的截图中，用户没有姓氏）
        await message.reply(f"你好, {user.full_name}")
```

![Добавлены несколько юзеров](images/messages/multiple_add.png)

请务必记住， `message.new_chat_members` 是一个列表，因为一个用户可以同时添加多个参与者。
另外，不要混淆 `message.from_user` 和 `message.new_chat_members` 字段。
第一个字段是主体，即执行操作的人。第二个字段是操作的对象。
例如，如果您看到的信息是 "Anna 添加了 Boris 和 Victor"，那么 `message.from_user` 就是关于 Anna 的信息，
而 `message.new_chat_members` 列表则包含关于 Boris 和 Victor 的信息。

!!! warning "不要完全依赖服务信息！"

    添加（new_chat_members）和离开（left_chat_members）服务消息有一个令人讨厌的特点：它们不可靠，也就是说，它们可能根本不会被创建。

    例如，当一个群组的成员达到约 10k 人时，new_chat_members 消息就会停止创建，而 left_chat_member 消息则会在成员达到 50 人时停止创建。

    随着 Bot API 5.0 的发布，开发人员现在有了**一种更可靠的方法**来查看任何规模的群组和频道中成员的输入/输出。不过，我们下次再[讨论这个问题](special-updates.md)。

## 技巧：在文本中隐藏链接 {: id="bonus" }

有些情况下，你想发送带有图片的长信息，但媒体文件标题的限制只有 1024 个字符，而普通文本信息的限制是 4096 个字符，而且在底部插入媒体链接看起来很难看。
此外，Telegram 在预览链接时，会先读取其中的元标签，因此发送的信息可能无法预览您想看到的内容。

为了解决这个问题，多年前人们发明了 HTML 标记中的 "隐藏链接 "方法。
其原理是，你可以在[零宽度](http://www.fileformat.info/info/unicode/char/200b/index.htm)的空间中放置链接，并在信息开头插入整个结构。对于观察者来说，信息中没有链接，但 Telegram 服务器会看到一切，并诚实地添加预览。

为此，aiogram 的开发人员甚至开发了一种特殊的辅助方法 `hide_link()` ：

```python
# 导入
from aiogram.utils.markdown import hide_link

@dp.message(Command("hidden_link"))
async def cmd_hidden_link(message: Message):
    await message.answer(
        f"{hide_link('https://telegra.ph/file/562a512448876923e28c3.png')}"
        f"Telegram 文档：*存在*\n"
        f"用户：*不要阅读文档\n"
        f"hi:"
    )
```

![Изображение со скрытой ссылкой](images/messages/hidden_link.png)

就到这里吧。下章再见！
<s><small>点赞、订阅、按铃。</small></s>