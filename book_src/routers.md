---
title: 路由器、多文件和机器人结构
description: 路由器、多文件和机器人结构
---

# 路由器、多文件和机器人结构

!!! info ""

    使用的 aiogram 版本： 3.1.1

在本章中，我们将熟悉 aiogram 3.x 的新功能--路由器，学习如何将代码分解成独立的组件，并形成基本的机器人结构，这将在接下来的章节和生活中派上用场。

## 应用程序的入口点 {: id="entrypoint" }

剧院从悬挂点开始，机器人从入口点开始。让它成为一个文件 `bot.py` 。我们将在其中定义异步函数 `main()` ，并在其中创建必要的对象并开始轮询。需要哪些对象？首先，当然是机器人，它可以有多个，但我们下次再讨论这个问题。其次是调度器。它接受来自 Telegram 的事件，并通过过滤器和 middlewares 将其分配给处理程序。

```python title="bot.py"
import asyncio
from aiogram import Bot, Dispatcher


# 启动机器人
async def main():
    bot = Bot(token="TOKEN")
    dp = Dispatcher()

    # 启动机器人，跳过所有累积的收件箱
    # 是的，即使你有轮询也可以调用这个方法
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
```

但这还不足以处理消息，我们还需要处理程序。我们想把它们放在其他文件中，这样就不用把几千行代码弄得一团糟了。在前几章中，我们所有的处理程序都是连接到派发器的，但现在它是在一个函数中，我们肯定不想让它成为一个全局对象。
我们该怎么办？这就需要帮助了......

## 路由器 {: id="routers" }

让我们打开 aiogram 3.x [官方文档](https://docs.aiogram.dev/en/dev-3.x/dispatcher/router.html) ，看看下面的图片：

![Несколько роутеров](https://docs.aiogram.dev/en/dev-3.x/_images/nested_routers_example.png)

我们看到了什么？ 

1. 调度器 - 是根路由器。
2. 处理程序依附于路由器。
3. 路由器可以嵌套，但它们之间只能单向通信。
4. 路由器开启（因此也是测试）的顺序是明确规定的。

在下图中，您可以看到更新程序搜索要执行的处理程序的顺序：

![порядок поиска апдейтом нужного хэндлера](https://docs.aiogram.dev/en/dev-3.x/_images/update_propagation_flow.png)

让我们编写一个具有两种功能的简单机器人：

1. 如果向机器人发送 `/start` ，它应发送一个问题和两个按钮，按钮上分别写有 "是" 和 "否"。
2. 如果向机器人发送任何其他文本、贴纸或 gif，它应回复信息类型的名称。

让我们从键盘开始：在文件 `bot.py` 旁创建一个目录 `keyboards` ，并在其中创建一个文件 `for_questions.py` ，然后编写一个函数来获得一个简单的键盘，在一行中包含 "是" 和 "否" 按钮：

```python title="keyboards/for_questions.py"
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_yes_no_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Да")
    kb.button(text="Нет")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)
```

这并不复杂，尤其是我们之前已经详细分析过键盘。现在，我们将在文件 `bot.py` 旁边创建另一个目录 `handlers` ，并在其中创建文件 `questions.py` 。

```python title="handlers/questions.py" hl_lines="7 9"
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.for_questions import get_yes_no_kb

router = Router()  # [1]

@router.message(Command("start"))  # [2]
async def cmd_start(message: Message):
    await message.answer(
        "你对自己的工作满意吗？",
        reply_markup=get_yes_no_kb()
    )

@router.message(F.text.lower() == "да")
async def answer_yes(message: Message):
    await message.answer(
        "这很酷！",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(F.text.lower() == "нет")
async def answer_no(message: Message):
    await message.answer(
        "真遗憾...",
        reply_markup=ReplyKeyboardRemove()
    )
```

请注意第 [1] 和 [2] 项。首先，我们在文件中创建了自己的模块级路由器，并将其连接到根路由器（调度器）。其次，处理程序是从本地路由器 "分支" 出来的。

同样，让我们用 `different_types.py` 处理程序制作第二个文件，在这里我们只需输出消息类型：

```python title="handlers/different_types.py"
from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text)
async def message_with_text(message: Message):
    await message.answer("这是一条短信！")

@router.message(F.sticker)
async def message_with_sticker(message: Message):
    await message.answer("这是一个贴纸！")

@router.message(F.animation)
async def message_with_gif(message: Message):
    await message.answer("是 GIF！")

```

最后，让我们回到 `bot.py` 中，导入路由器和处理程序文件，并将它们插入调度程序：

```python title="bot.py" hl_lines="3 11 12"
import asyncio
from aiogram import Bot, Dispatcher
from handlers import questions, different_types


# 运行机器人
async def main():
    bot = Bot(token="TOKEN")
    dp = Dispatcher()

    dp.include_routers(questions.router, different_types.router)

    # 每行注册一个路由器的替代方案
    # dp.include_router(questions.router)
    # dp.include_router(different_types.router)

    # 启动机器人并跳过所有累积的传入消息
    # 是的，即使进行了轮询，也可以调用该方法。
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
```

我们只需从 `handlers/` 目录中导入文件，并将这些文件中的路由器连接到调度程序。同样，导入的顺序也很重要！如果我们交换路由器注册，机器人就会以 "这是一条文本消息！" 来回应 `/start` 命令，因为 `message_with_text()` 函数将是第一个成功通过所有过滤器的函数。不过，我们稍后会讨论过滤器本身，现在让我们再考虑一个问题。


## 结构 {: id="conclusion" }

我们设法在不影响机器人工作的情况下，将其整齐地划分为不同的文件。文件和目录树大致如下（此处特意省略了一些不重要的文件）：

```
├── bot.py
├── handlers
│   ├── different_types.py
│   └── questions.py
├── keyboards
│   └── for_questions.py
```

今后，我们将沿用这一结构，并为过滤器、中间件、数据库文件等添加新的目录。