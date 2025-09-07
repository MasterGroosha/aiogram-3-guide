---
title: Routers, Multi-file Structure and Bot Architecture
description: Routers, Multi-file Structure and Bot Architecture
---

# Routers, Multi-file Structure and Bot Architecture

!!! info ""
    aiogram version used: 3.7.0  
    Tested on aiogram version: 3.21.0 | 07.07.2025

In this chapter, we'll explore a new feature of aiogram 3.x — routers, learn how to split our code into separate components, and establish a basic bot structure that will be useful in subsequent chapters and in general practice.

## Application Entry Point {: id="entrypoint" }

The theater begins with a cloakroom, and a bot begins with an entry point. Let's call it the `bot.py` file. In it, we'll define an asynchronous function `main()` where we'll create the necessary objects and start polling. What objects are necessary? First, of course, the bot. There could be several bots, but that's a topic for another time. Second, the dispatcher. It handles receiving events from Telegram and distributing them to handlers through filters and middlewares.

```python title="bot.py"
import asyncio
from aiogram import Bot, Dispatcher


# Bot launch
async def main():
    bot = Bot(token="TOKEN")
    dp = Dispatcher()

    # Start the bot and skip all accumulated incoming updates
    # Yes, this method can be called even if you're using polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
```

But to process messages, this isn't enough; we also need handlers. We want to place them in other files to avoid having thousands of lines in a single file. In previous chapters, all our handlers were attached to the dispatcher, but now it's inside a function, and we definitely don't want to make it a global object.  
What should we do? This is where routers come to the rescue...

## Routers {: id="routers" }

Let's refer to the [official documentation](https://docs.aiogram.dev/en/dev-3.x/dispatcher/router.html) of aiogram 3.x and look at the following image:

![Multiple routers](https://docs.aiogram.dev/en/dev-3.x/_images/nested_routers_example.png)

What do we see?

1. The dispatcher is the root router.
2. Handlers are attached to routers.
3. Routers can be nested, but there's only a one-way connection between them.
4. The order of inclusion (and, consequently, checking) of routers is explicitly defined.

The next image shows the order in which an update searches for the appropriate handler to execute:

![Order of search for the appropriate handler](https://docs.aiogram.dev/en/dev-3.x/_images/update_propagation_flow.png)

Let's write a simple bot with two features:

1. If the bot receives `/start`, it should send a question and two buttons labeled "Yes" and "No".
2. If the bot receives any other text, sticker, or GIF, it should reply with the name of the message type.

Let's start with the keyboard: create a `keyboards` directory next to the `bot.py` file, and inside it a file `for_questions.py`, where we'll write a function to get a simple keyboard with "Yes" and "No" buttons in one row:

```python title="keyboards/for_questions.py"
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_yes_no_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Yes")
    kb.button(text="No")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)
```

Nothing complicated, especially since we covered keyboards in detail earlier. Now, let's create another directory `handlers` next to the `bot.py` file, and inside it a file `questions.py`.

```python title="handlers/questions.py" hl_lines="7 9"
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.for_questions import get_yes_no_kb

router = Router()  # [1]

@router.message(Command("start"))  # [2]
async def cmd_start(message: Message):
    await message.answer(
        "Are you satisfied with your job?",
        reply_markup=get_yes_no_kb()
    )

@router.message(F.text.lower() == "yes")
async def answer_yes(message: Message):
    await message.answer(
        "That's great!",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(F.text.lower() == "no")
async def answer_no(message: Message):
    await message.answer(
        "That's a pity...",
        reply_markup=ReplyKeyboardRemove()
    )
```

Let's pay attention to points [1] and [2]. First, we created our own module-level router in the file, and later we'll attach it to the root router (dispatcher). Second, handlers are now "branching off" from the local router.

Similarly, let's create a second file with handlers `different_types.py`, where we'll simply display the message type:

```python title="handlers/different_types.py"
from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text)
async def message_with_text(message: Message):
    await message.answer("This is a text message!")

@router.message(F.sticker)
async def message_with_sticker(message: Message):
    await message.answer("This is a sticker!")

@router.message(F.animation)
async def message_with_gif(message: Message):
    await message.answer("This is a GIF!")

```

Finally, let's return to our `bot.py`, import the files with routers and handlers, and connect them to the dispatcher:

```python title="bot.py" hl_lines="3 11 12"
import asyncio
from aiogram import Bot, Dispatcher
from handlers import questions, different_types


# Bot launch
async def main():
    bot = Bot(token="TOKEN")
    dp = Dispatcher()

    dp.include_routers(questions.router, different_types.router)

    # Alternative way to register routers one per line
    # dp.include_router(questions.router)
    # dp.include_router(different_types.router)

    # Start the bot and skip all accumulated incoming updates
    # Yes, this method can be called even if you're using polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
```

We simply import files from the `handlers/` directory and connect the routers from these files to the dispatcher. And here again, the order of imports is important! If we swap the registration of routers, the bot will respond to the `/start` command with the phrase "This is a text message!" because the `message_with_text()` function will be the first to successfully pass all filters. But we'll discuss filters a bit later, and for now, let's consider one more question.

## Conclusion {: id="conclusion" }

We've managed to neatly separate the bot into different files without disrupting its functionality. The approximate file and directory tree looks like this (some files not essential for the example are deliberately omitted here):

```
├── bot.py
├── handlers
│   ├── different_types.py
│   └── questions.py
├── keyboards
│   └── for_questions.py
```

Moving forward, we'll stick to this structure, plus add new directories for filters, middlewares, files for working with databases, etc.
