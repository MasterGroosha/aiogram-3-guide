---
title: Working with Messages
description: Working with Messages
---

!!! warning "An important warning about translation!"
    Hello! This message is from the translator [VAI || Programmer](https://github.com/Vadim-Khristenko).
    Please keep in mind that this page is still being translated.

# Working with Messages

!!! info ""
    The version of aiogram used: 3.7.0

In this chapter, we will learn how to apply different types of formatting to messages 
and work with media files.

## Text {: id="text" }
Processing text messages is arguably one of the most important actions for most bots. 
Text can be used to express almost anything, and you want to present the information _beautifully_. 
Developers have three methods of text formatting at their disposal: 
HTML, Markdown, and MarkdownV2. The most advanced among them are HTML and MarkdownV2, 
“classic” Markdown supports fewer features and is no longer used in aiogram.

Before we look at the ways of working with text in aiogram, it's necessary to mention 
an important distinction between aiogram 3.x and 2.x: in "version two" by default, only 
text messages were processed, but in "version three," messages of any type are processed. 
To be more precise, here is how you now need to handle text messages exclusively:

```python
# before (with decorator)
@dp.message_handler()
async def func_name(...)

# before (with function-registrar)
dp.register_message_handler(func_name)

# now (with decorator)
from aiogram import F
@dp.message(F.text)
async def func_name(...)

# now (with function-registrar)
dp.message.register(func_name, F.text)
```

We will talk about the "magic filter" **F** in [another chapter](filters-and-middlewares.md).

### Formatted Output {: id="formatting-options" }

The choice of formatting when sending messages is determined by the `parse_mode` argument, for example:
```python
from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode

# If you don't specify the F.text filter,
# then the handler will even trigger on an image with the caption /test
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

![Hello world with different formatting](../images/en/messages/l02_1.png)

If a particular formatting is used throughout the bot, specifying the `parse_mode` argument each time can be quite cumbersome. 
Fortunately, in aiogram, you can set default bot parameters. To do this, create a `DefaultBotProperties` object 
and pass the required settings into it:

```python
from aiogram.client.default import DefaultBotProperties

bot = Bot(
    token="123:abcxyz",
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
        # there are many other interesting settings here
    )
)
bot = Bot(token="123:abcxyz", parse_mode="HTML")

# somewhere in a function...
await message.answer("Message with <u>HTML markup</u>")
# to explicitly disable formatting in a specific request, 
# pass parse_mode=None
await message.answer(
    "Message without <s>any markup</s>", 
    parse_mode=None
)
```

![Default formatting type setting](../images/en/messages/l02_2.png)
