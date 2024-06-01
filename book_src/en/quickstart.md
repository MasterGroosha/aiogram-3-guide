---
title: Getting Started with aiogram
description: Getting Started with aiogram
---

# Getting Started with aiogram

!!! info ""
    The version of aiogram used: 3.7.0

!!! warning "Some details are intentionally simplified!"
    The author of this book is convinced that along with theory, there should be practice. 
    To simplify the replication of the code provided below, it was necessary to use approaches 
    suitable only for local development and learning.

    Thus, for example, in all or almost all chapters, the bot's token will be indicated 
    directly in the source texts. This is a **bad** approach because it can lead to the token being disclosed 
    if you forget to remove it before uploading the code to a public repository (e.g., GitHub).

    Or, sometimes, data storage structures located exclusively in memory (dictionaries, lists...) will be used. 
    In reality, such objects are undesirable, as stopping the bot will lead to the irreversible loss of data.

    Also, polling is chosen as the mechanism for receiving updates from Telegram 
    because it is guaranteed to work in the vast majority of environments and suits almost all developers.

    **It is important to remember that the author's goal is to explain specifically how to work with the Telegram Bot API
    using aiogram, not to teach all of Computer Science in its entirety.**

## Terminology {: id="glossary" }

To communicate using the same concepts, let's introduce some terms to avoid confusion moving forward:

* DM — direct messages, in the context of a bot this is a one-on-one conversation with a user, not a group/channel.
* Chat — a general term for DMs, groups, supergroups, and channels.
* Update — any event from [this list](https://core.telegram.org/bots/api#update): 
messages, edited messages, callbacks, inline queries, payments, adding bots to groups, etc.
* Handler — an asynchronous function that receives the next update from the dispatcher/router 
and processes it.
* Dispatcher — an object that handles receiving updates from Telegram and subsequently chooses a handler 
to process the received update.
* Router — similar to the dispatcher, but responsible for a subset of handlers. 
**It can be said that the dispatcher is the root router**.
* Filter — an expression that usually returns True or False and affects whether a handler will be called or not.
* Middleware — a layer that is inserted into the processing of updates.

## Installation {: id="installation" }

First, let's create a directory for the bot, set up a virtual environment (venv) there, and
install the [aiogram](https://github.com/aiogram/aiogram) library.  
Let's check that Python version 3.9 is installed (if you know that you have version 3.9 or higher, you can skip this section):

```plain
[groosha@main lesson_01]$ python3.9
Python 3.9.9 (main, Jan 11 2022, 16:35:07) 
[GCC 11.1.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> exit()
[groosha@main lesson_01]$ 
```

Now let's create a `requirements.txt` file, in which we will specify the version of aiogram we are using. 
We will also need the pydantic-settings library for configuration files.
!!! important "About aiogram versions"
    This chapter uses aiogram **3.x**. Before you start, 
    I recommend checking the [release channel](https://t.me/aiogram_live) of the library to see if there is a newer version available. 
    Any newer version starting with the number 3 will do, as aiogram 2.x will not be considered anymore and is deemed outdated.

```plain
[groosha@main 01_quickstart]$ python3.11 -m venv venv
[groosha@main 01_quickstart]$ echo "aiogram<4.0" > requirements.txt
[groosha@main 01_quickstart]$ echo "pydantic-settings" >> requirements.txt
[groosha@main 01_quickstart]$ source venv/bin/activate
(venv) [groosha@main 01_quickstart]$ pip install -r requirements.txt 
# ...here a bunch of lines about installation...
Successfully installed ...here a long list...
[groosha@main 01_quickstart]$
```

Note the "venv" prefix in the terminal. It indicates that we are inside a virtual environment named "venv".
Let's verify that inside venv the command `python` still points to the same Python 3.11:  
```plain
(venv) [groosha@main 01_quickstart]$ python
Python 3.11.9 (main, Jan 11 2024, 16:35:07) 
[GCC 11.1.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> exit()
(venv) [groosha@main 01_quickstart]$ deactivate 
[groosha@main 01_quickstart]$ 
```

Using the last `deactivate` command, we exited venv so that it doesn't interfere with us now.

!!! info ""
    If you use PyCharm for writing bots, I also recommend installing the third-party 
    [Pydantic](https://plugins.jetbrains.com/plugin/12861-pydantic) plugin to support code autocompletion 
    in Telegram objects.

## First Bot {: id="hello-world" }

Let's create a `bot.py` file with a basic bot template using aiogram:
```python title="bot.py"
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

# Enable logging to avoid missing important messages
logging.basicConfig(level=logging.INFO)
# Bot object
bot = Bot(token="12345678:AaBbCcDdEeFfGgHh")
# Dispatcher
dp = Dispatcher()

# Handler for the /start command
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")

# Start polling for new updates
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
```

The first thing to note is that aiogram is an asynchronous library, so your handlers must also be asynchronous, 
and you need to put the **await** keyword before API method calls, as these calls return [coroutines](https://docs.python.org/3/library/asyncio-task.html#coroutines).

!!! info "Asynchronous programming in Python"
    Don't neglect the official documentation!  
    A great tutorial on asyncio is available [on the Python website](https://docs.python.org/3/library/asyncio-task.html)

If you have previously worked with another library for Telegram, for example, pyTelegramBotAPI, 
then the concept of handlers (event processors) will immediately become clear to you. 
The difference is that in aiogram, handlers are managed by the dispatcher. The dispatcher registers handler functions, 
further limiting the list of events that call them through filters. After receiving the next update (event from Telegram), 
the dispatcher will select the appropriate processing function that matches all the filters, 
for example, "processing messages that are images, in a chat with ID x and with a caption length of y". 
If two functions have logically identical filters, the one that was registered first will be called.

To register a function as a message handler, you need to do one of two things:  
1. Attach a [decorator](https://devpractice.ru/python-lesson-19-decorators/) to it, as in the example above. 
We will get acquainted with various types of decorators later.  
2. Directly call the registration method on the dispatcher or router.
