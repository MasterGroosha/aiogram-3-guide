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

### Input Escaping {: id="input-escaping" }

It's not uncommon for situations to arise where the final text of a bot's message is unknown in advance 
and is formed based on some external data: the user's name, their input, etc. 
Let’s write a handler for the `/hello` command that will greet the user by their full name 
(`first_name + last_name`), for example: “Hello, Ivan Ivanov”:

```python
from aiogram.filters import Command

@dp.message(Command("hello"))
async def cmd_hello(message: Message):
    await message.answer(
        f"Hello, <b>{message.from_user.full_name}</b>",
        parse_mode=ParseMode.HTML
    )
```

And it seems all good, the bot greets users:

![The /hello command in action](../images/en/messages/cmd_hello_before.png)
![The /hello command in action with user Ivan Ivanov](../images/en/messages/cmd_hello_ivan_before.png)

But then comes a user with the name &lt;Slavik777&gt; and the bot remains silent! And the logs show the following:
`aiogram.exceptions.TelegramBadRequest: Telegram server says - Bad Request: can't parse entities: 
Unsupported start tag "Slavik777" at byte offset 7`

Oops, we have the HTML formatting mode set, and Telegram tries to parse &lt;Slavik777&gt; as an HTML tag. That’s not good. 
But there are several solutions to this problem. The first one: escape the passed values.

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

The second one is a bit more complicated but more advanced: use a special tool that will 
collect the text and information on which parts of it should be formatted separately.

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

In the example above, the `**content.as_kwargs()` construction will return the arguments `text`, `entities`, `parse_mode`, and 
substitute them in the call to `answer()`.

![The /hello command in action after fix](../images/en/messages/cmd_hello_after.png)

The mentioned formatting tool is quite complex, 
[the official documentation](https://docs.aiogram.dev/en/latest/utils/formatting.html) demonstrates convenient display 
of complex constructs, for example:

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

![Advanced example](../images/en/messages/advanced_example.png)

!!! info ""
    You can learn more about the different formatting methods and supported tags 
    [in the Bot API documentation](https://core.telegram.org/bots/api#formatting-options).
