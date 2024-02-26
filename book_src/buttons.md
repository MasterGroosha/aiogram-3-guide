---
title: 按钮
description: 按钮
---

# 按钮

!!! info ""

    使用的 aiogram 版本： 3.1.1

在本章中，我们将了解 Telegram 机器人的一大特色--按钮。首先，为了避免混淆，我们先来定义一下名称。
附着在设备屏幕底部的按钮称为**普通按钮**，直接附着在消息上的按钮称为**内联按钮**。请再看一次图片：

![Два вида кнопок](images/buttons/l03_1.png)

## 普通按钮 {: id="reply-buttons" }
### 按钮模版 {: id="reply-as-text" }

这种按钮与 Bot API 一起出现在遥远的 2015 年，只不过是消息模板（少数特殊情况除外，稍后详述）。
原理很简单：写在按钮上的内容将发送到当前聊天。因此，为了处理按下的按钮，机器人必须识别收到的文本信息。

让我们编写一个处理程序，当按下 `/start` 命令时，它将发送一条带有两个按钮的信息：

```python
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [types.KeyboardButton(text="С пюрешкой")],
        [types.KeyboardButton(text="Без пюрешки")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
    await message.answer("如何食用炸肉排?", reply_markup=keyboard)
```

!!! info ""

    尽管 Telegram Bot API 允许指定字符串而不是 [KeyboardButton](https://core.telegram.org/bots/api#keyboardbutton) 对象，
    但当尝试使用字符串时，aiogram 3.x 会抛出一个验证错误，这不是一个错误，而是一个功能。

    现在就接受 🤷‍♂️ 吧。

好了，让我们启动机器人，看看这些巨大的按钮有多神奇吧：

![Очень большие обычные кнопки](images/buttons/l03_2.png)

看起来很难看。首先，我想把按钮变小，其次，把它们水平放置。

它们为什么这么大？因为默认情况下，`按钮` 键盘在智能手机上所占的空间应与普通字母键盘相同。
要使按钮变小，您需要为键盘对象指定一个附加参数 `resize_keyboard=True` 。

但如何用水平键替换垂直键呢？
从 Bot API 的角度来看，[键盘](https://core.telegram.org/bots/api#replykeyboardmarkup)是一个由按钮组成的数组，或者更简单地说，是一个由行组成的数组。
让我们重写代码，使其看起来更美观，同时添加一个参数 `input_field_placeholder` ，当常规键盘激活时，该参数将替换空输入行中的文本：

```python
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="配土豆泥"),
            types.KeyboardButton(text="没有土豆泥")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="选择送货方式"
    )
    await message.answer("如何食用炸肉排?", reply_markup=keyboard)
```

真是美不胜收：

![Кнопки в один ряд](images/buttons/l03_3.png)

剩下的工作就是教会机器人在按下这些按钮时做出反应。
如上所述，有必要检查全文是否匹配。让我们借助神奇的 F 过滤器来完成这项工作，我们将在下一章详细讨论该[过滤器](filters-and-middlewares.md#magic-filters)：

```python
# новый импорт!
from aiogram import F

@dp.message(F.text.lower() == "配土豆泥")
async def with_puree(message: types.Message):
    await message.reply("很好的选择！")

@dp.message(F.text.lower() == "没有土豆泥")
async def without_puree(message: types.Message):
    await message.reply("太没品味了！")
```

![Реакция на нажатие кнопок](images/buttons/l03_4.png)

要删除按钮，您需要发送一条带有特殊 `删除` 键盘的新信息，如 `ReplyKeyboardRemove` 。
例如： `await message.reply("很好的选择！", reply_markup=types.ReplyKeyboardRemove())` 。

### 键盘生成器 {: id="reply-builder" }

为了更动态地生成按钮，我们可以使用键盘生成器。我们需要以下方法：

- `add(<KeyboardButton>)` — 将按钮添加到汇编程序的内存中；
- `adjust(int1, int2, int3...)` — 按 `int1、int2、int3...` 按钮处理字符串；
- `as_markup()` — 返回一个完成的键盘对象；
- `button(<params>)` — 添加一个带有指定参数的按钮，按钮类型（回复或内联）将自动确定。

让我们创建一个 4×4 的数字键盘：

```python
# новый импорт!
from aiogram.utils.keyboard import ReplyKeyboardBuilder

@dp.message(Command("reply_builder"))
async def reply_builder(message: types.Message):
    builder = ReplyKeyboardBuilder()
    for i in range(1, 17):
        builder.add(types.KeyboardButton(text=str(i)))
    builder.adjust(4)
    await message.answer(
        "选择一个数字：",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )
```

![Результат работы сборщика кнопок](images/buttons/reply_builder.png)


!!! info ""

    [常规键盘对象](https://core.telegram.org/bots/api#replykeyboardmarkup)有两个更有用的选项：
    `one_time_keyboard` 用于在按键被按下后自动隐藏按键；
    `selective` 用于仅向组中的某些成员显示键盘。这两个选项的使用有待独立研究。

### 特殊的普通按钮 {: id="reply-special" }

在撰写本章时，Telegram 中有六种特殊的常规按钮不属于常规信息模板。它们是为以下目的设计的：

- 发送当前地理位置；
- 向联系人发送电话号码；
- 创建调查/测验；
- 选择并发送符合所需标准的机器人用户数据；
- 选择并向机器人发送符合所需标准的（超级）群组或频道数据；
- 启动网络应用程序（WebApp）。

让我们来详细谈谈它们。

**发送当前地理位置。**这里一切都很简单：发送用户所在位置的坐标。这将是一个静态地理位置，而不是自动更新的实时位置。 当然，聪明的用户可以伪造自己的位置，有时甚至在系统层面（Android）。

**发送带有电话号码的联系人。**当用户点击按钮（事先确认）时，他就会向机器人发送带有电话号码的联系人。 同样狡猾的用户也可以忽略按钮并发送任何联系人，但在这种情况下，他们是可以被控制的：只需检查处理程序或过滤器中的 `message.contact.user_id == message.from_user.id` 等号即可。

**创建投票/测验。**点击按钮后，系统会提示用户创建投票或测验，然后将其发送到当前聊天。必须传递 [KeyboardButtonPollType](https://core.telegram.org/bots/api#keyboardbuttonpolltype) 对象和一个可选参数 `type` 以指定投票类型（投票或测验）。

**根据所需条件选择用户数据并发送给机器人。**显示一个窗口，用于从点击按钮的用户的聊天列表中选择用户。必须传递 [KeyboardButtonRequestUser](https://core.telegram.org/bots/api#keyboardbuttonrequestuser) 对象，其中必须指定由任何方法和条件生成的请求 ID，例如 `机器人`、`已订阅Telegram Premium`等。选择用户后，机器人将收到一条 [UserShared](https://core.telegram.org/bots/api#usershared) 类型的服务消息。

**选择并发送符合所需条件的聊天机器人。**显示一个窗口，用于从按下按钮的用户的聊天列表中选择用户。需要传递 [KeyboardButtonRequestChat](https://core.telegram.org/bots/api#keyboardbuttonrequestchat) 对象，其中需要指定由任何方法和标准生成的请求 ID，例如 `群组或频道`、`用户是聊天创建者`等。选择用户后，机器人将收到一条 [ChatShared](https://core.telegram.org/bots/api#chatshared) 类型的服务消息。

**启动网络应用程序（WebApp）。**单击按钮可打开 [WebApp](https://core.telegram.org/bots/webapps)。您需要传递一个 [WebAppInfo](https://core.telegram.org/bots/api#webappinfo) 对象。本书暂时不涉及 WebApp。

不过，查看一次代码会更容易：

```python
@dp.message(Command("special_buttons"))
async def cmd_special_buttons(message: types.Message):
    builder = ReplyKeyboardBuilder()
    # 行方法可以显式地生成多个按钮
    # 通过一个或多个按钮。例如第一行
    # 将由两个按钮组成...
    builder.row(
        types.KeyboardButton(text="请求地理位置", request_location=True),
        types.KeyboardButton(text="请求联系方式", request_contact=True)
    )
    # ... 其中一个的第二个 ...
    builder.row(types.KeyboardButton(
        text="创建测验",
        request_poll=types.KeyboardButtonPollType(type="quiz"))
    )
    # ... 第三个也是二分之一
    builder.row(
        types.KeyboardButton(
            text="选择高级用户",
            request_user=types.KeyboardButtonRequestUser(
                request_id=1,
                user_is_premium=True
            )
        ),
        types.KeyboardButton(
            text="选择一个有论坛的超级群组",
            request_chat=types.KeyboardButtonRequestChat(
                request_id=2,
                chat_is_channel=False,
                chat_is_forum=True
            )
        )
    )
    # 还没有 WebApps，抱歉：(

    await message.answer(
        "选择一项操作：",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )
```

![Специальные обычные кнопки](images/buttons/special_buttons.png)

最后是两个空白处理程序，用于接受底部两个按钮的按键操作：

```python
# 导入
from aiogram import F

@dp.message(F.user_shared)
async def on_user_shared(message: types.Message):
    print(
        f"Request {message.user_shared.request_id}. "
        f"User ID: {message.user_shared.user_id}"
    )


@dp.message(F.chat_shared)
async def on_user_shared(message: types.Message):
    print(
        f"Request {message.chat_shared.request_id}. "
        f"User ID: {message.chat_shared.chat_id}"
    )
```


## 内联按钮 {: id="inline-buttons" }
### URL {: id="url-buttons" }

与普通按钮不同的是，内联按钮并不附着在屏幕底部，而是附着在与之一起发送的信息上。
在本章中，我们将介绍两种类型的按钮：URL 和回调。另一种类型--Switch--将在有关[内联模式](inline-mode.md)的章节中讨论。

!!! info ""

    书中的登录和支付按钮将完全不予考虑。

最简单的内嵌按钮是 URL 类型，即 "链接"。仅支持 HTTP(S) 和 tg:// 协议。

```python
# 导入
from aiogram.utils.keyboard import InlineKeyboardBuilder

@dp.message(Command("inline_url"))
async def cmd_inline_url(message: types.Message, bot: Bot):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="GitHub", url="https://github.com")
    )
    builder.row(types.InlineKeyboardButton(
        text="Telegram",
        url="tg://resolve?domain=telegram")
    )

    # 为了能够显示 ID 按钮，
    # 用户必须有 False 标志 has_private_forwards
    user_id = 1234567890
    chat_info = await bot.get_chat(user_id)
    if not chat_info.has_private_forwards:
        builder.row(types.InlineKeyboardButton(
            text="一些用户",
            url=f"tg://user?id={user_id}")
        )

    await message.answer(
        '选择链接',
        reply_markup=builder.as_markup(),
    )
```

让我们分别关注一下中间的代码块。重点是，2019 年 3 月，Telegram 开发人员在转发消息中添加了[禁用转发到用户个人资料](https://telegram.org/blog/unsend-privacy-emoji#anonymous-forwarding)的功能。当尝试使用已禁用转发转换的用户 ID 创建 URL 按钮时，机器人将收到 `Bad Request: BUTTON_USER_PRIVACY_RESTRICTED` 错误。因此，在显示这样的按钮之前，有必要找出上述设置的状态。为此，您可以调用 [getChat](https://core.telegram.org/bots/api#getchat) 方法并检查响应中 `has_private_forwards` 字段的状态。如果它等于 `True` ，那么尝试添加 URL-ID 按钮将导致错误。

### 回调 {: id="callback-buttons" }

关于 URL 按钮已经没有什么可讨论的了，让我们继续今天节目的重头戏--回调按钮。这是一个非常强大的功能，几乎随处可见。帖子的反应按钮（赞）、@BotFather的菜单等。关键在于：回调按钮有一个特殊的值（数据），您的应用程序可以通过它来识别按下的是什么以及应该做什么。选择正确的数据**非常重要**！值得注意的是，与普通按钮不同，按下返回按钮几乎可以做任何事情，从订购披萨到在超级计算机集群上运行计算。

让我们编写一个处理程序，在 `/random` 命令上发送带有 callback 按钮的消息：

```python
@dp.message(Command("random"))
async def cmd_random(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="点击我",
        callback_data="random_value")
    )
    await message.answer(
        "点击按钮让机器人发送 1 到 10 之间的数字",
        reply_markup=builder.as_markup()
    )
```

但我们如何处理推送呢？如果之前我们使用 `message` 处理程序来处理接收到的消息，那么现在我们将使用 `callback_query` 处理程序来处理回弹。我们将重点关注按钮的 `值`，即其数据：

```python
@dp.callback_query(F.data == "random_value")
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.answer(str(randint(1, 10)))
```

![Реакция на нажатие колбэк-кнопки](images/buttons/l03_5.png)

哎呀，那个钟是什么？原来 Telegram 服务器正在等待我们确认回调的发送，否则它会显示一个特殊图标 30 秒。要隐藏时钟，您需要调用回调的 `answer()` 方法（或使用 API 方法 `answer_callback_query()` ）。一般情况下，您可以不向 `answer()` 方法传递任何信息，但可以调用一个特殊框（弹出在顶部或屏幕顶部）：

```python
@dp.callback_query(F.data == "random_value")
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.answer(str(randint(1, 10)))
    await callback.answer(
        text="感谢您使用机器人！",
        show_alert=True
    )
    # 或者只是 await callback.answer()
```

![Всплывающее окно при нажатии на колбэк-кнопку](images/buttons/l03_6.png)

读者可能会有一个问题：在处理过程中，应该在什么时候使用 `answer()` 方法响应回调？一般来说，最主要的是记得通知 Telegram 接收回调请求，但我建议将 `answer()` 调用放在最后，原因如下：如果在处理回调过程中发生错误，机器人遇到未处理的异常，用户将看到一个半分钟内不会消失的时钟，并意识到出了问题。否则，时钟就会消失，而用户将被蒙在鼓里，不知道自己的请求是否成功。

!!! info "请注意"

    在 `send_random_value` 函数中，我们不是在 `message` 上调用 `answer()` 方法，而是在 `callback.message` 上调用 `answer()` 方法。
    这是因为回调处理程序不处理消息（[Message](https://core.telegram.org/bots/api#message) 类型），而是处理回调（[CallbackQuery](https://core.telegram.org/bots/api#callbackquery) 类型），回调有不同的字段，消息本身只是其中的一部分。
    还要注意的是， `message` 是附加了按钮的消息（即此类消息的发送者是机器人本身）。
    如果您想知道是谁点击了按钮，请参阅 `from` 字段（在您的代码中将是 `callback.from_user` ，因为 `from` 在 Python 中是保留字）。

!!! warning "关于 callback 中的 `message` 对象"

    如果消息是从[内联模式](https://mastergroosha.github.io/aiogram-3-guide/inline-mode/)发送的，回调的 `message` 字段将为空。
    除非事先将其保存在某个地方，否则将无法检索此类信息的内容。

下面我们来看一个更复杂的例子。让用户看到一条数字为 0 的信息，底部有三个按钮：+1、-1 和确认。通过前两个按钮，用户可以编辑数字，而最后一个按钮则会删除整个键盘，固定更改。我们将在内存中的字典中存储数值（我们将在下次讨论 _有限状态机_）。

```python
# 用户数据存储在这里。
# 由于这是内存中的字典，重新启动时会被清除
user_data = {}

def get_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton(text="-1", callback_data="num_decr"),
            types.InlineKeyboardButton(text="+1", callback_data="num_incr")
        ],
        [types.InlineKeyboardButton(text="确认", callback_data="num_finish")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def update_num_text(message: types.Message, new_value: int):
    await message.edit_text(
        f"输入一个数字: {new_value}",
        reply_markup=get_keyboard()
    )

        
@dp.message(Command("numbers"))
async def cmd_numbers(message: types.Message):
    user_data[message.from_user.id] = 0
    await message.answer("输入数字: 0", reply_markup=get_keyboard())

    
@dp.callback_query(F.data.startswith("num_"))
async def callbacks_num(callback: types.CallbackQuery):
    user_value = user_data.get(callback.from_user.id, 0)
    action = callback.data.split("_")[1]

    if action == "incr":
        user_data[callback.from_user.id] = user_value+1
        await update_num_text(callback.message, user_value+1)
    elif action == "decr":
        user_data[callback.from_user.id] = user_value-1
        await update_num_text(callback.message, user_value-1)
    elif action == "finish":
        await callback.message.edit_text(f"全部的: {user_value}")

    await callback.answer()
```

一切似乎都很顺利：

![Всё работает?](images/buttons/l03_7.png)

但现在让我们设想一下，一个聪明的用户做了以下操作：调用 `/numbers` （值为 0），将值增加到 1，再次调用 `/numbers` （值重置为 0），然后编辑并点击第一篇帖子上的 "+1 "按钮。结果如何？机器人会诚实地发送一个请求，以编辑值为 1 的文本，但由于该帖子已经有了数字 1，机器人 API 会返回一个错误，即新旧文本相同，机器人会捕获一个异常：
`Bad Request: message is not modified: specified new message content and reply markup are exactly the same 
as a current content and reply markup of the message`

![Ошибка BadRequest при определённых обстоятельствах](images/buttons/l03_8.png)

在尝试编辑信息时，您可能会经常遇到这个错误。一般来说，这种错误通常表示生成/更新信息中数据的逻辑出现了问题，但有时，就像上面的例子一样，它也可能是预料之中的行为。

在这种情况下，我们将忽略整个错误，因为我们只关心最终结果，而最终结果肯定是正确的。**MessageNotModified** 错误属于 Bad Request 类别，因此我们可以选择：忽略整个此类错误，或者捕获整个 BadRequest 类别并尝试从错误文本中找出具体的错误原因。为了不使示例过于复杂，我们将采用第一种方法，并对 `update_num_text()` 函数稍作更新：

```python
# 新的导入
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest

async def update_num_text(message: types.Message, new_value: int):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            f"输入一个数字: {new_value}",
            reply_markup=get_keyboard()
        )
```

如果您现在尝试重复上面的示例，机器人将直接忽略该代码块中指定的异常。

### 回调工厂 {: id="callback-factory" }

当您使用一些具有共同前缀的简单拼写，如 `order_1 , order_2 ...` 时，您可能会认为调用 `split()` 并用一些分隔符分割字符串非常简单。你可能会认为，调用 `split()` 并用分隔符分割字符串非常简单。现在想象一下，您需要存储的不仅仅是一个值，而是三个值： `order_1_1994_2731519` 。这里的文章、价格和数量是什么？或者是生产年份？字符串分区开始变得可怕： `.split("_")[2]` 。为什么不是 1 或 3？

在某些情况下，您需要对此类回调数据的内容进行结构化处理，而 aiogram 提供了一种解决方案！您可以创建 `CallbackData` 类型的对象，指定前缀，描述结构，然后框架就会独立收集包含回调数据的字符串，更重要的是，它还会正确解析传入的值。让我们再举一个具体的例子；让我们创建一个带有前缀 `fabnum` 和两个字段 `action` 和 `value` 的类 `NumbersCallbackFactory` 。 `action` 字段指定了要做的事情，是改变值（更改）还是提交（完成），而 value 字段则表示要改变值多少。默认值为无，因为 `完成` 操作不需要更改 delta。代码

```python
# 导入
from typing import Optional
from aiogram.filters.callback_data import CallbackData

class NumbersCallbackFactory(CallbackData, prefix="fabnum"):
    action: str
    value: Optional[int] = None
```

我们的类必须继承自 `CallbackData` 并接受一个前缀值。前缀是开头的共同子串，框架将据此确定 `callback` 中的结构。

现在让我们编写键盘生成函数。这里我们需要 `button()` 方法，它将自动创建一个所需类型的按钮，我们只需传递参数即可。作为参数 `callback_data` 而不是字符串，我们将指定一个类 `NumbersCallbackFactory` 的实例：

```python
def get_keyboard_fab():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="-2", callback_data=NumbersCallbackFactory(action="change", value=-2)
    )
    builder.button(
        text="-1", callback_data=NumbersCallbackFactory(action="change", value=-1)
    )
    builder.button(
        text="+1", callback_data=NumbersCallbackFactory(action="change", value=1)
    )
    builder.button(
        text="+2", callback_data=NumbersCallbackFactory(action="change", value=2)
    )
    builder.button(
        text="确认", callback_data=NumbersCallbackFactory(action="finish")
    )
    # 将 4 个按钮对齐成一排，形成 4 + 1
    builder.adjust(4)
    return builder.as_markup()
```

发送信息和编辑信息的方法保持不变（我们将在名称和命令中添加后缀 `_fab` ）：

```python
async def update_num_text_fab(message: types.Message, new_value: int):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            f"输入数字: {new_value}",
            reply_markup=get_keyboard_fab()
        )

@dp.message(Command("numbers_fab"))
async def cmd_numbers_fab(message: types.Message):
    user_data[message.from_user.id] = 0
    await message.answer("输入数字: 0", reply_markup=get_keyboard_fab())
```

最后，让我们进入正题--处理回卷。为此，我们需要将捕捉回车的类通过调用方法 `filter()` 传递给装饰器。此外，还有一个名称为 `callback_data` （名称必须完全相同！）的附加参数，其类型与被过滤类相同：

```python
@dp.callback_query(NumbersCallbackFactory.filter())
async def callbacks_num_change_fab(
        callback: types.CallbackQuery, 
        callback_data: NumbersCallbackFactory
):
    # 当前值
    user_value = user_data.get(callback.from_user.id, 0)
    # 如果需要更改号码
    if callback_data.action == "change":
        user_data[callback.from_user.id] = user_value + callback_data.value
        await update_num_text_fab(callback.message, user_value + callback_data.value)
    # 如果数字需要修正
    else:
        await callback.message.edit_text(f"总计: {user_value}")
    await callback.answer()
```

让我们的处理程序更具体一些，为数字按钮和 `确认` 按钮制作一个单独的处理程序。我们将通过 `action` 值进行过滤，aiogram 3.x 的 "神奇过滤器 "将帮助我们做到这一点。说真的，这就是它们的名字：神奇过滤器。我们将在下一章详细介绍这种神奇的滤镜，但现在我们只需使用这种 `魔法过滤`，并认为它是理所当然的：

```python
# 导入
from magic_filter import F

# 按下其中一个按钮: -2, -1, +1, +2
@dp.callback_query(NumbersCallbackFactory.filter(F.action == "change"))
async def callbacks_num_change_fab(
        callback: types.CallbackQuery, 
        callback_data: NumbersCallbackFactory
):
    # 当前值
    user_value = user_data.get(callback.from_user.id, 0)

    user_data[callback.from_user.id] = user_value + callback_data.value
    await update_num_text_fab(callback.message, user_value + callback_data.value)
    await callback.answer()


# 按下 "确认" 按钮
@dp.callback_query(NumbersCallbackFactory.filter(F.action == "finish"))
async def callbacks_num_finish_fab(callback: types.CallbackQuery):
    # 当前值
    user_value = user_data.get(callback.from_user.id, 0)

    await callback.message.edit_text(f"总计: {user_value}")
    await callback.answer()
```

![Фабрика колбэков](images/buttons/callback_factory.png)

乍一看，我们的工作似乎很复杂，但实际上，callback 工厂允许您创建高级 callback 按钮，并方便地将代码分割成逻辑实体。

### 回调应答 {: id="callback-autoreply" }

如果您有大量的 callback 句柄，而您需要对它们进行应答或以同样的方式进行应答，那么您可以使用一种特殊的[中变体](filters-and-middlewares.md#middlewares)来简化您的工作。一般来说，我们会单独讨论这种方法，但现在我们先熟悉一下。
1
因此，最简单的方法是在创建调度程序后添加这样一行：

```python
# 不要忘记导入
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

dp = Dispatcher()
dp.callback_query.middleware(CallbackAnswerMiddleware())
```

在这种情况下，处理程序执行后，aiogram 会自动响应 [callback](https://github.com/aiogram/aiogram/blob/5adaf7a567e976da64e418eee5df31682ad2496c/aiogram/utils/callback_answer.py#L133-L137)。您可以覆盖默认设置并指定自己的设置，例如

```python
dp.callback_query.middleware(
    CallbackAnswerMiddleware(
        pre=True, text="准备好！", show_alert=True
    )
)
```

唉，所有回调处理程序都有相同响应的情况非常罕见。幸运的是，在特定处理程序中覆盖 中间件 行为非常容易：只需抛出 callback_answer 参数并为其设置新值即可：

```python
# 导入!
from aiogram.utils.callback_answer import CallbackAnswer

@dp.callback_query()
async def my_handler(callback: CallbackQuery, callback_answer: CallbackAnswer):
    ... # 这是一些代码
    if <everything is ok>:
        callback_answer.text = "太棒了!"
    else:
        callback_answer.text = "出了些问题。稍后再试"
        callback_answer.cache_time = 10
    ... # 这是一些代码
```

**重要提示：** 如果在 middlewares 上设置了 `pre=True` 标志，此方法将不起作用。在这种情况下，有必要通过标志重新定义 middlewares 的参数集，我们稍后会[详细介绍](filters-and-middlewares.md#flags)：

```python
from aiogram import flags
from aiogram.utils.callback_answer import CallbackAnswer

@dp.callback_query()
@flags.callback_answer(pre=False)  # 覆盖预标记
async def my_handler(callback: CallbackQuery, callback_answer: CallbackAnswer):
    ... # 这是一些代码
    if <everything is ok>:
        callback_answer.text = "现在可以看到这段文字!"
    ... # 这是一些代码
```

按钮介绍到此结束。