---
title: 了解aiogram
description: 了解aiogram
---

# 了解aiogram

!!! info ""
    使用的 aiogram 版本： 3.1.1

!!! warning "一些细节刻意简化！"
    本书作者深信，理论之外还应有实践。为了尽可能方便地重复下面的代码，我们不得不采用只适合本地开发和培训的方法。

    例如，在所有或几乎所有章节中，机器人令牌都会直接在源代码中指定。这是一种糟糕的做法，因为如果在将代码上传到公共仓库（如 GitHub）之前忘记删除，就会导致令牌泄露。

    有时，完全位于 RAM 中的结构（字典、列表......）也会被用作数据存储空间。事实上，这样的对象并不可取，因为停止机器人会导致无法挽回的数据丢失。

    我们还选择了轮询作为从 Telegram 接收更新的机制，因为它能保证在绝大多数环境下正常工作，几乎适合所有开发人员。

    **重要的是要记住，作者的目的是准确解释如何使用aiogram来使用Telegram Bot API，而不是解释整个计算机科学的多样性。**

## 术语 {: id="glossary" }

为了用同样的术语说话，让我们来介绍一些术语，以免今后混淆：

* PM — 是私人信息，在机器人中是与用户一对一的对话，而不是群组/频道。
* 聊天 — 是 PM、群组、超级群组和频道的统称。
* 更新 — 此[列表](https://core.telegram.org/bots/api#update)中的任何事件： 发帖、帖子编辑、回帖、内联请求、付款、向组添加机器人等。
* 处理程序 — 是一个异步函数，用于接收来自调度器/路由器的下一次更新并进行处理。
* Dispatcher(调度器) — 是一个从 Telegram 接收更新，然后选择一个句柄来处理接收到的更新的对象。
* 路由器 — 与调度程序类似，但负责多个处理程序的子集。
**可以说，调度器是根路由器。**.
* 过滤器 — 是一个表达式，通常返回 `True` 或 `False`，并影响处理程序是否被调用。
* 中间件 — 是嵌入到更新处理中的一个层。

## 安装 {: id="installation" }

首先，为机器人创建一个目录，创建一个虚拟环境（以下简称 venv），并安装 [aiogram](https://github.com/aiogram/aiogram) 库。
让我们检查是否安装了 Python 3.9 版本（如果已经安装了 3.9 及以上版本，可以跳过本节）：

```plain
[groosha@main lesson_01]$ python3.9
Python 3.9.9 (main, Jan 11 2022, 16:35:07) 
[GCC 11.1.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> exit()
[groosha@main lesson_01]$ 
```

现在创建一个 `requirements.txt` 文件，在其中指定我们使用的 aiogram 版本。配置文件还需要使用 python-dotenv 库。
!!! important "关于 aiogram 版本"
    本章使用的是 aiogram 3.x，在开始之前，我建议查看库的发布渠道，以获取更新的版本。任何以 **3** 开头的新版本都可以使用，因为 aiogram 2.x 不再被考虑使用，已被视为弃用版本。

```plain
[groosha@main 01_quickstart]$ python3.9 -m venv venv
[groosha@main 01_quickstart]$ echo "aiogram<4.0" > requirements.txt
[groosha@main 01_quickstart]$ echo "python-dotenv==1.0.0" >> requirements.txt
[groosha@main 01_quickstart]$ source venv/bin/activate
(venv) [groosha@main 01_quickstart]$ pip install -r requirements.txt 
# ...здесь куча строк про установку...
Successfully installed ...тут длинный список...
[groosha@main 01_quickstart]$
```

注意终端中的前缀 `venv`。这表明我们正处于一个名为 `venv` 的虚拟环境中。让我们检查一下 `venv` 中的 `python` 命令调用是否指向同一个 `Python 3.9`： 
```plain
(venv) [groosha@main 01_quickstart]$ python
Python 3.9.9 (main, Jan 11 2022, 16:35:07) 
[GCC 11.1.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> exit()
(venv) [groosha@main 01_quickstart]$ deactivate 
[groosha@main 01_quickstart]$ 
```

随着最后一条 `deactivate` 命令的下达，我们离开了 `VENV`，这样他就不会来打扰我们了。

!!! info ""
    如果您使用 PyCharm 编写机器人，我还建议您安装第三方 [Pydantic](https://plugins.jetbrains.com/plugin/12861-pydantic) 插件，以支持 Telegram 对象中的自动完成代码。

## 第一个机器人 {: id="hello-world" }

让我们在 aiogram 上创建一个带有基本机器人模板的 `bot.py` 文件：
```python title="bot.py"
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

# 启用日志记录功能，以免错过重要信息
logging.basicConfig(level=logging.INFO)
# 机器人对象
bot = Bot(token="12345678:AaBbCcDdEeFfGgHh")
# 调度器
dp = Dispatcher()

# /start 命令的处理程序
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")

# 开始轮询新的更新
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
```

首先：aiogram 是一个异步库，所以你的处理程序也应该是异步的，而且你应该在 API 方法调用之前加上 `await` 关键字，因为这些调用会返回 [coroutines](https://docs.python.org/3/library/asyncio-task.html#coroutines)。

!!! info "Python 异步编程"
    正式文件也不容忽视！
    Python 网站上有关于 [asyncio](https://docs.python.org/3/library/asyncio-task.html) 的精彩教程。

如果你过去使用过其他 Telegram 库，例如 pyTelegramBotAPI，你就会立即理解处理程序（事件处理程序）的概念，唯一的区别是，在 aiogram 中，处理程序由调度程序管理。

调度程序会注册处理函数，并通过过滤器限制调用这些函数的事件列表。在接收到下一次更新（来自 Telegram 的事件）后，调度程序将选择符合所有筛选条件的必要处理函数，例如 *处理 ID 为 x、签名长度为 ygk 的聊天图像信息*。如果两个函数的过滤器相同，则会调用较早注册的那个。

要将函数注册为消息处理程序，必须完成以下两件事之一： 

1. 挂上一个装饰器，如上面的例子。稍后我们将了解不同类型的[装饰器](https://devpractice.ru/python-lesson-19-decorators/)。
2. 直接调用调度器或路由器的注册方法。

请看下面的代码：
```python
# /test1 命令的处理程序
@dp.message(Command("test1"))
async def cmd_test1(message: types.Message):
    await message.reply("Test 1")

# /test2 命令的处理程序
async def cmd_test2(message: types.Message):
    await message.reply("Test 2")
```

让我们用它运行一个机器人： 
![/test2 命令不起作用](images/quickstart/l01_1.jpg)

处理程序 `cmd_test2` 将无法工作，因为调度程序不知道它。让我们修复这个错误，并单独注册该函数：
```python
# /test2 命令的处理程序
async def cmd_test2(message: types.Message):
    await message.reply("Test 2")

# 其他地方，例如在 main() 函数中：
dp.message.register(cmd_test2, Command("test2"))
```

让我们再次运行机器人： 
![Обе команды работают](images/quickstart/l01_2.jpg)

## 语法糖 {: id="sugar" }

为了使代码更简洁易读，aiogram 扩展了标准 Telegram 对象的功能。例如，你可以写 `message.answer(...)` 或 `message.reply(...)` 来代替 `bot.send_message(...)` 。在后两种情况下，您不需要替换 `chat_id` ，因为它被认为与原始信息中的内容相同。

`answer` 和 `reply` 之间的区别很简单：第一种方法只是向同一个聊天室发送消息，第二种方法是 `回复` 来自 `message` 的消息：
```python
@dp.message(Command("answer"))
async def cmd_answer(message: types.Message):
    await message.answer("答案很简单")


@dp.message(Command("reply"))
async def cmd_reply(message: types.Message):
    await message.reply('这是一个有 "答案 "的答案')
```
![Разница между message.answer() и message.reply()](images/quickstart/l01_3.jpg)

此外，大多数消息类型都有 `answer_{type}` 或 `reply_{type}` 等辅助方法：
```python
@dp.message(Command("dice"))
async def cmd_dice(message: types.Message):
    await message.answer_dice(emoji="🎲")
```

!!! info "'message: types.Message' 是什么?"
    Python 是一种解释型语言，具有强动态类型，因此没有像 C++ 或 Java 那样的[内置类型检查](https://zh.wikipedia.org/zh-cn/%E9%A1%9E%E5%9E%8B%E7%B3%BB%E7%B5%B1#%E5%9E%8B%E5%88%A5%E6%AA%A2%E6%9F%A5)。
    不过，从 3.5 版开始，该语言引入了对[类型提示](https://docs.python.org/zh-cn/3/library/typing.html)的支持，这样各种检查器和集成开发环境（如 PyCharm）就能分析所用值的类型，并在传递错误值时提示程序员。
    在本例中，`types.Message`提示告诉 PyCharm，`message`变量具有 aiogram 库的`types`模块中描述的`Message`类型（参见代码开头的导入）。
    这样，IDE 就能即时建议属性和函数。

调用`/dice`时，机器人将向同一个聊天室发送骰子。当然，如果您想将骰子发送到其他聊天室，就必须用老方法调用`await bot.send_dice(...)`。
但是，`bot`对象（Bot 类的实例）在特定函数的作用域中可能不可用。在 aiogram 3.x 中，接收更新的机器人对象会被隐式地抛入处理程序，并可作为`bot`的参数到达。
假设你想在`/dice`命令中发送一个立方体，但不是发送到同一个聊天室，而是发送到 ID 为 -100123456789 的频道。让我们重写之前的函数：

```python
# 不要忘记导入
from aiogram.enums.dice_emoji import DiceEmoji

@dp.message(Command("dice"))
async def cmd_dice(message: types.Message, bot: Bot):
    await bot.send_dice(-100123456789, emoji=DiceEmoji.DICE)
```

## 传输附加参数 {: id="pass-extras" }

有时，运行机器人时可能需要传递一个或多个附加值。这可能是一个变量、一个配置对象、一个列表、一个时间戳或其他任何东西。为此，只需将这些数据作为命名（kwargs）参数传递给调度程序，或者像处理字典一样赋值。

该功能最适用于传递单个实例中的对象，在机器人操作过程中不会发生变化（即只读）。如果值会随时间发生变化，请记住这只适用于[可变对象](https://mathspp.com/blog/pydonts/pass-by-value-reference-and-assignment)。要在处理程序中获取值，只需将其指定为参数即可。我们来看一个例子：

```python
# 在别的地方
# 例如，在应用程序入口点
from datetime import datetime

# bot = ...
dp = Dispatcher()
dp["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
await dp.start_polling(bot, mylist=[1, 2, 3])


@dp.message(Command("add_to_list"))
async def cmd_add_to_list(message: types.Message, mylist: list[int]):
    mylist.append(7)
    await message.answer("添加了数字 7")


@dp.message(Command("show_list"))
async def cmd_show_list(message: types.Message, mylist: list[int]):
    await message.answer(f"列表清单: {mylist}")

    
@dp.message(Command("info"))
async def cmd_info(message: types.Message, started_at: str):
    await message.answer(f"机器人启动于 {started_at}")
```

现在，`started_at`变量和`mylist`列表可以在不同的处理程序中读取和写入。如果您需要为每次更新（例如 DBMS 会话对象）抛出唯一值，请查看 [中间件](filters-and-middlewares.md#middlewares)。

![Аргумент mylist может быть изменён между вызовами](images/quickstart/extra-args.png)

## 配置文件

为了避免直接在代码中存储令牌（如果你想把机器人上传到公共仓库怎么办？有一种观点认为，环境变量足以满足销售的需要，但在本书中，我们将使用单独的 `.env` 文件来简化我们的生活，并为读者节省部署演示项目的时间。

因此，让我们在 `bot.py` 旁边创建一个单独的文件 `config_reader.py` ，内容如下

```python title="config_reader.py"
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    # 最好使用 SecretStr 而不是 str 
    # 对于敏感数据，例如机器人令牌
    bot_token: SecretStr

    # 从 pydantic 的第二个版本开始，设置了 settings 类设置
    # 通过 model_config
    # 在这种情况下，将使用读取的 .env 文件
    # 使用 UTF-8 编码
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


# 导入文件时，它会立即创建
# 并且配置对象已验证，
# 可从不同地方进一步导入
config = Settings()
```

现在，让我们稍微编辑一下 `bot.py` ：

```python title="bot.py"
# 导入
from config_reader import config

# 对于 Secret* 类型的记录，必须
# 调用 get_secret_value() 方法
# 来获取实际内容，而不是 '*******'
bot = Bot(token=config.bot_token.get_secret_value())
```

最后，让我们创建一个文件 `.env` （文件开头有一个点）来描述机器人令牌：

```title=".env"
BOT_TOKEN = 0000000000:AaBbCcDdEeFfGgHhIiJjKkLlMmNn
```

如果一切操作正确，python-dotenv 将在启动时从 `.env` 文件加载变量，pydantic 将验证这些变量，并使用所需的令牌成功创建机器人对象。

关于该库的介绍到此为止，在接下来的章节中，我们将讨论 aiogram 和 Telegram Bot API 的其他 "功能"。
