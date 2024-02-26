---
title: 有限状态机（FSM）
description: 有限状态机（FSM）
---

# 有限状态机（FSM） {: id="fsm-start" }

!!! info ""

    使用的 aiogram 版本： 3.1.1

## 理论 {: id="theory" }

本章我们将讨论机器人的另一个重要功能：**对话系统**。遗憾的是，并不是机器人中的所有操作都能在一条消息或命令中完成。假设有一个约会机器人，在注册时，你必须指定自己的姓名、年龄并发送一张脸部照片。当然，您可以要求用户发送一张照片，并在标题中指定所有数据，但这对处理和请求重新输入很不方便。
现在，让我们设想一个逐步输入数据的过程，在开始时，机器人会 "`开启`" 等待特定用户提供某些信息的模式，然后每一步都会检查输入的数据，并在 `/cancel` 命令下停止等待下一步，返回主模式。请看下图：

![Процесс, состоящий из трёх этапов](images/fsm/l04_1.svg)

**绿色箭头**表示无差错地完成所有步骤，**蓝色箭头**表示保持当前状态并等待重新进入（例如，如果用户指定他/她的年龄为 250 岁，则应再次请求年龄），**红色箭头**表示由于 `/cancel` 命令或任何其他表示取消的命令而退出整个流程。

上述方案中的过程在算法理论中被称为**有限状态机**（或 FSM - Finite State Machine）。

!!! info "对话生成器"

    在本章练习了 FSM 之后，你可能会感觉到要得到一个复杂的动作分支链需要做很多事情。幸运的是，**Tishka** 提供的 [aiogram-dialog](https://github.com/Tishka17/aiogram_dialog) 库可以简化状态机的工作。

## 实践 {: id="practice" }

aiogram 中的有限状态机机制已经支持各种后端，用于存储与机器人对话的各个阶段之间的状态（不过，没有人阻止你编写自己的后端），
除了状态本身之外，你还可以存储任意数据，例如上文所述的姓名和年龄，以便日后在其他地方使用。
可用的 FSM 存储器列表可以在 [aiogram 仓库](https://github.com/aiogram/aiogram/tree/dev-3.x/aiogram/fsm/storage)中找到，但在本章中我们将使用最简单的后端 [MemoryStorage](https://github.com/aiogram/aiogram/blob/dev-3.x/aiogram/fsm/storage/memory.py)，
它将所有数据存储在 RAM 中。MemoryStorage 是示例的理想选择，但不建议在实际项目中使用，因为 MemoryStorage 会将所有数据存储在 RAM 中，
而不会重置到磁盘。值得注意的是，
有限自动机不仅可用于消息处理程序（ `message_handler` , `edited_message_handler` ），
还可用于 callback 和内联模式。

例如，我们将编写一个在咖啡馆点菜和点饮料的模拟器。

### 创建步骤 {: id="define-states" }

在介绍 FSM 之前，我们先来介绍一个简单的函数，它可以生成一个普通的键盘，键盘上的按钮排成一行，稍后会派上用场：

```python title="keyboards/simple_row.py"
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    """
    Создаёт реплай-клавиатуру с кнопками в один ряд
    :param items: список текстов для кнопок
    :return: объект реплай-клавиатуры
    """
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)
```

让我们来看看 "订餐" 步骤的描述。让我们创建一个文件 `handlers/ordering_food.py` ，在这个文件中，我们将描述菜肴清单及其大小（在现实生活中，这些信息可以从某个数据库中动态加载）：

```python
# Эти значения далее будут подставляться в итоговый текст, отсюда 
# такая на первый взгляд странная форма прилагательных
available_food_names = ["Суши", "Спагетти", "Хачапури"]
available_food_sizes = ["Маленькую", "Среднюю", "Большую"]
```

现在，让我们来描述一个特定流程（选餐）的所有可能 "状态"。
我们可以这样描述：用户调用 `/food` 命令，机器人回复一条要求选餐的消息，并进入 *等待为特定用户选餐* 的状态。
一旦用户做出选择，机器人在此状态下会验证输入的正确性，然后决定是再次请求输入（不改变状态），还是进入下一步 *等待选择份量* 。
如果用户在此输入的数据也正确无误，机器人就会显示最终结果（订单内容）并重置状态。
本章后面我们将学习如何使用 `/cancel` 命令在任意步骤强制重置状态。

### 步骤 1 {: id="step-1" }

因此，让我们直接进入状态描述。
要存储状态，我们需要创建一个继承自 `StatesGroup` 类的类，在这个类中，我们需要通过为 `State` 类的实例赋值来创建变量：

```python
class OrderFood(StatesGroup):
    choosing_food_name = State()
    choosing_food_size = State()
```

让我们编写一个第一步处理程序，在用户没有设置任何统计信息的情况下对 `/food` 命令作出反应：

```python hl_lines="4 10"
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

@router.message(StateFilter(None), Command("food"))
async def cmd_food(message: Message, state: FSMContext):
    await message.answer(
        text="Выберите блюдо:",
        reply_markup=make_row_keyboard(available_food_names)
    )
    # Устанавливаем пользователю состояние "выбирает название"
    await state.set_state(OrderFood.choosing_food_name)
```

要使用 FSM 机制，我们需要向处理程序抛出一个名为 `state` 的参数，该参数的类型为 `FSMContext` 。
在最后一行，我们明确告诉机器人进入 `OrderFood` 组的 `choosing_food_name` 状态。

!!! warning "Отличие от aiogram 2.x"

    在 aiogram 2.x 中，没有状态过滤器意味着 "仅在没有显式暴露状态的情况下"（换句话说， `state=None` ）。
    在 aiogram 3.x 中，没有状态过滤器意味着 "在任何状态下"。回想一下，在基于内容的消息统计中也使用了类似的三元组方法。

接下来，让我们编写一个处理程序，捕捉列表中的一个食物选项：

```python linenums="1"
@router.message(
    OrderFood.choosing_food_name, 
    F.text.in_(available_food_names)
)
async def food_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_food=message.text.lower())
    await message.answer(
        text="Спасибо. Теперь, пожалуйста, выберите размер порции:",
        reply_markup=make_row_keyboard(available_food_sizes)
    )
    await state.set_state(OrderFood.choosing_food_size)
```

让我们仔细看看处理程序中的一些元素。筛选器（第 2-3 行）告诉我们，
只有当用户处于状态 `OrderFood.choosing_food_name` 且消息文本与列表 `available_food_names` 中的一个元素匹配时，
才会触发下面的函数。在第 6 行中，我们将数据（消息文本）写入 FSM 存储器，
该数据对于 (`chat_id`, `user_id`) 对来说是唯一的（这有一个细微差别，稍后再谈）。
最后，在第 11 行，我们让用户进入 `OrderFood.choosing_food_size` 状态。

如果用户决定自己输入，而不使用键盘怎么办？
在这种情况下，您应该告知用户错误并让他再试一次。
机器人开发新手往往会在这个时候问："如何让用户处于相同的状态？"
答案很简单：要让用户保持当前状态，只需不改变它（状态）即可，即 _什么都不做_。

让我们再编写一个处理程序，它将只对 `OrderFood.choosing_food_name` 状态进行过滤，
而不对文本进行过滤。如果我们把它放在 `food_chosen()` 函数下面，
我们就会得到 "在 `choosing_food_name` 状态下，对所有文本做出反应， 前一个处理程序捕获的文本除外"（换句话说，"捕获所有错误的变体"）。

```python
@router.message(OrderFood.choosing_food_name)
async def food_chosen_incorrectly(message: Message):
    await message.answer(
        text="Я не знаю такого блюда.\n\n"
             "Пожалуйста, выберите одно из названий из списка ниже:",
        reply_markup=make_row_keyboard(available_food_names)
    )
```

### 步骤 2 {: id="step-2" }

第二步也是最后一步是处理用户输入的份量。与上一步类似，让我们制作两个处理程序（正确答案和错误答案），但在第一个处理程序中，我们将添加有关订单的摘要信息的选择：

```python hl_lines="3 9"
@router.message(OrderFood.choosing_food_size, F.text.in_(available_food_sizes))
async def food_size_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await message.answer(
        text=f"Вы выбрали {message.text.lower()} порцию {user_data['chosen_food']}.\n"
             f"Попробуйте теперь заказать напитки: /drinks",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


@router.message(OrderFood.choosing_food_size)
async def food_size_chosen_incorrectly(message: Message):
    await message.answer(
        text="Я не знаю такого размера порции.\n\n"
             "Пожалуйста, выберите один из вариантов из списка ниже:",
        reply_markup=make_row_keyboard(available_food_sizes)
    )
```

第 3 行中的 `get_data()` 调用会返回一个特定聊天室中特定用户的存储对象。
我们从中获取菜名的存储值，并将其放入消息中。栈的 clear() 方法会将用户返回到 "`None`" 状态，并删除所有存储数据。
如果只想清除状态或只想覆盖数据怎么办？让我们来看看 aiogram 3.x 源代码中 `clear()` 函数的定义：

```python
class FSMContext:
    # Часть кода пропущена

    async def clear(self) -> None:
        await self.set_state(state=None)
        await self.set_data({})
```

现在你知道如何清除一件东西了吧 :)

选择饮料的步骤非常相似。你可以自己试试，或者查看本章的源代码。

食品订购处理人员档案全文：

```python title="handlers/ordering_food.py"
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.simple_row import make_row_keyboard

router = Router()

# Эти значения далее будут подставляться в итоговый текст, отсюда
# такая на первый взгляд странная форма прилагательных
available_food_names = ["Суши", "Спагетти", "Хачапури"]
available_food_sizes = ["Маленькую", "Среднюю", "Большую"]


class OrderFood(StatesGroup):
    choosing_food_name = State()
    choosing_food_size = State()


@router.message(Command("food"))
async def cmd_food(message: Message, state: FSMContext):
    await message.answer(
        text="Выберите блюдо:",
        reply_markup=make_row_keyboard(available_food_names)
    )
    # Устанавливаем пользователю состояние "выбирает название"
    await state.set_state(OrderFood.choosing_food_name)

# Этап выбора блюда #


@router.message(OrderFood.choosing_food_name, F.text.in_(available_food_names))
async def food_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_food=message.text.lower())
    await message.answer(
        text="Спасибо. Теперь, пожалуйста, выберите размер порции:",
        reply_markup=make_row_keyboard(available_food_sizes)
    )
    await state.set_state(OrderFood.choosing_food_size)


# В целом, никто не мешает указывать стейты полностью строками
# Это может пригодиться, если по какой-то причине 
# ваши названия стейтов генерируются в рантайме (но зачем?)
@router.message(StateFilter("OrderFood:choosing_food_name"))
async def food_chosen_incorrectly(message: Message):
    await message.answer(
        text="Я не знаю такого блюда.\n\n"
             "Пожалуйста, выберите одно из названий из списка ниже:",
        reply_markup=make_row_keyboard(available_food_names)
    )

# Этап выбора размера порции и отображение сводной информации #


@router.message(OrderFood.choosing_food_size, F.text.in_(available_food_sizes))
async def food_size_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await message.answer(
        text=f"Вы выбрали {message.text.lower()} порцию {user_data['chosen_food']}.\n"
             f"Попробуйте теперь заказать напитки: /drinks",
        reply_markup=ReplyKeyboardRemove()
    )
    # Сброс состояния и сохранённых данных у пользователя
    await state.clear()


@router.message(OrderFood.choosing_food_size)
async def food_size_chosen_incorrectly(message: Message):
    await message.answer(
        text="Я не знаю такого размера порции.\n\n"
             "Пожалуйста, выберите один из вариантов из списка ниже:",
        reply_markup=make_row_keyboard(available_food_sizes)
    )
```

### 一般命令 {: id="common-commands" }

既然我们谈论的是重置状态，那么就让我们在 `/start` 文件中实现 `handlers/common.py` 命令和 "`取消`" 操作的处理程序。
在第一种情况下，应显示一些欢迎/帮助文本，而对于取消操作，我们将编写两个处理程序：当用户未处于任何状态时和当用户处于任何状态时。

所有功能均保证无状态、无数据，并移除常用键盘（如果突然有的话）：

```python title="handlers/common.py"
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, ReplyKeyboardRemove

router = Router()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Выберите, что хотите заказать: "
             "блюда (/food) или напитки (/drinks).",
        reply_markup=ReplyKeyboardRemove()
    )


# Нетрудно догадаться, что следующие два хэндлера можно 
# спокойно объединить в один, но для полноты картины оставим так

# default_state - это то же самое, что и StateFilter(None)
@router.message(StateFilter(None), Command(commands=["cancel"]))
@router.message(default_state, F.text.lower() == "отмена")
async def cmd_cancel_no_state(message: Message, state: FSMContext):
    # Стейт сбрасывать не нужно, удалим только данные
    await state.set_data({})
    await message.answer(
        text="Нечего отменять",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command(commands=["cancel"]))
@router.message(F.text.lower() == "отмена")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Действие отменено",
        reply_markup=ReplyKeyboardRemove()
    )

```

### 文件 bot.py {: id="entrypoint" }

最后，让我们看看入口点--连接了所有进口和路由器的文件 `bot.py` ：

```python title="bot.py"
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# файл config_reader.py можно взять из репозитория
# пример — в первой главе
from config_reader import config
from handlers import common, ordering_food


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # Если не указать storage, то по умолчанию всё равно будет MemoryStorage
    # Но явное лучше неявного =]
    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(config.bot_token.get_secret_value())

    dp.include_router(common.router)
    dp.include_router(ordering_food.router)
    # сюда импортируйте ваш собственный роутер для напитков

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
```

### FSM 的类别 {: id="strategies" }

Aiogram 3.x 为有限自动机机制带来了一项不同寻常但又十分有趣的创新--FSM 策略。它们允许我们重新定义舵和数据的成对逻辑。总共有四种策略，分别是

* **USER_IN_CHAT** — 默认策略。每个用户在每次聊天中的状态和数据都不同。也就是说，用户在不同群组以及与机器人聊天时的状态和数据都不同。
* **CHAT** — 统计数据和数据在整个聊天过程中是通用的。在聊天室中，差异并不明显，但在群组中，所有参与者的统计信息和数据都是一样的。
* **GLOBAL_USER** — 同一用户在所有聊天中将拥有相同的统计信息和数据。
* **USER_IN_TOPIC** — 用户可以根据超级群组论坛的[主题](https://telegram.org/blog/topics-in-groups-collectible-usernames#topics-in-groups)获得不同的统计信息。

老实说，我想不出 **GLOBAL_USER** 有什么好的用处，但 **CHAT** 对在群组中执行各种游戏的机器人可能很有用。如果您知道有趣的用途，请在聊天中告诉我们！

举个例子，订餐机器人莫名其妙地加入了一个群组，并使用了聊天策略。为了实现这一点，我们需要对 `bot.py` 文件进行少量编辑：

```python
# новый импорт
from aiogram.fsm.strategy import FSMStrategy

async def main():
    # тут код
    dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.CHAT)
    # тут тоже код
```

启动机器人后，请群组中的人与之互动：

![Все пользователи для бота на одно лицо](images/fsm/fsm_chat_strategy.png)

看起来很奇怪，不是吗？

现在，有了有限自动机的知识，你就可以无所畏惧地编写带有对话系统的机器人了。