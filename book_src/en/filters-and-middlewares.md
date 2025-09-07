---
title: Filters and Middlewares
description: Filters and Middlewares
t_status: complete_except_images
---

# Filters and Middlewares

!!! info ""
    aiogram version used: 3.14.0

It's time to figure out how filters and middlewares work in aiogram 3.x, and also to get acquainted with 
the "lambda expression killer" of the framework — _magic filters_.

## Filters {: id="filters" }

### Why do we need filters? {: id="why-filters" }

If you've written your [first bot](quickstart.md#hello-world), then congratulations: you've already used filters, 
just built-in ones, not custom ones. Yes, that `Command("start")` is actually a filter. They are needed 
to ensure that the next update from Telegram goes to the right handler, i.e., where it [the update] is expected.

Let's look at the simplest example to understand the importance of filters. Let's say we have users Alice with ID 111 
and Bob with ID 777. And there's a bot that responds to any text message from our two friends with some 
motivational phrase, while rejecting everyone else:

```python
from random import choice

@router.message(F.text)
async def my_text_handler(message: Message):
    phrases = [
        "Hi! You look great :)",
        "Hello, today will be a great day!",
        "Hi there)) smile :)"
    ]
    if message.from_user.id in (111, 777):
        await message.answer(choice(phrases))
    else:
        await message.answer("I don't talk to you!")
```

Then at some point, we decide that we need to make a more personalized greeting for each of our friends, 
and for this we split our handler into three: for Alice, for Bob, and for everyone else:

```python
@router.message(F.text)
async def greet_alice(message: Message):
    # print("Handler for Alice")
    phrases = [
        "Hi, {name}. You look gorgeous today!",
        "You're the smartest, {name}",
    ]
    if message.from_user.id == 111:
        await message.answer(
            choice(phrases).format(name="Alice")
        )

@router.message(F.text)
async def greet_bob(message: Message):
    phrases = [
        "Hi, {name}. You're the strongest!",
        "You're cool, {name}!",
    ]
    if message.from_user.id == 777:
        await message.answer(
            choice(phrases).format(name="Bob")
        )

@router.message(F.text)
async def stranger_go_away(message: Message):
    if message.from_user.id not in (111, 777):
        await message.answer("I don't talk to you!")
```

With this setup, Alice will receive messages and be happy. But everyone else won't get anything because 
the code will always go into the `greet_alice()` function and not pass the `if message.from_user.id == 111` condition. 
You can easily verify this by uncommenting the `print()` call.

But why is that? The answer is simple: any text message will first go through the `F.text` check above the 
`greet_alice()` function, this check will return `True` and the update will go into this function, from where, not passing the internal 
condition `if`, it will exit and fade into oblivion.

To avoid such issues, filters exist. In reality, the correct check would be 
"text message AND user ID 111". Then, when Bob with ID 777 writes to the bot, the combination of filters 
would return False, and the router would go on to check the next handler where both filters would return True and the update would land in the handler. 
Perhaps at first glance the above sounds very complicated, but by the end of this chapter you'll understand how to properly organize 
such a check.

### Filters as classes {: id="filters-as-classes" }

Unlike aiogram 2.x, in "version 3" there is no longer a **ChatTypeFilter** class filter for a specific chat type 
(private, group, supergroup, or channel). Let's write it ourselves. Let's say the user will have the ability to specify the desired type 
either as a string or as a list. The latter can be useful when we're interested in several types at once, 
for example, groups and supergroups.

Our application entry point, namely the `bot.py` file, looks familiar:

```python title="bot.py"
import asyncio

from aiogram import Bot, Dispatcher


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

Next to it, let's create a `filters` directory, and inside it a file `chat_type.py`:

```python title="filters/chat_type.py" hl_lines="7 8 11"
from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message


class ChatTypeFilter(BaseFilter):  # [1]
    def __init__(self, chat_type: Union[str, list]): # [2]
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool:  # [3]
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type
```

Let's pay attention to the highlighted lines:

1. Our filters inherit from the base class `BaseFilter`
2. In the class constructor, we can set future filter arguments. In this case, we declare the presence of one
   argument `chat_type`, which can be either a string (`str`) or a list (`list`).
3. All the action happens in the `__call__()` method, which is triggered when an instance of the 
   `ChatTypeFilter()` class is called [as a function](https://docs.python.org/3/reference/datamodel.html?highlight=__call__#object.__call__). 
   Inside there's nothing special: we check the type of the passed object and call the appropriate check. 
   We aim for the filter to return a boolean value, since only the handler whose filters all returned `True` will be executed next.

Now let's write a couple of handlers in which we'll send a dice of the corresponding type in response to the `/dice` and `/basketball` commands, but only in a group. We create a file `handlers/group_games.py` and write some elementary code:

```python title="handlers/group_games.py" hl_lines="3 6 11 12 19 20"
from aiogram import Router
from aiogram.enums.dice_emoji import DiceEmoji
from aiogram.types import Message
from aiogram.filters import Command

from filters.chat_type import ChatTypeFilter

router = Router()


@router.message(
    ChatTypeFilter(chat_type=["group", "supergroup"]),
    Command(commands=["dice"]),
)
async def cmd_dice_in_group(message: Message):
    await message.answer_dice(emoji=DiceEmoji.DICE)


@router.message(
    ChatTypeFilter(chat_type=["group", "supergroup"]),
    Command(commands=["basketball"]),
)
async def cmd_basketball_in_group(message: Message):
    await message.answer_dice(emoji=DiceEmoji.BASKETBALL)
```

Well, let's break it down.  
First, we imported the built-in `Command` filter and our freshly written 
`ChatTypeFilter`.  
Second, we passed our filter as a positional argument to the decorator, specifying 
the desired chat type(s) as arguments.  
Third, in aiogram 2.x you were used to filtering commands as `commands=...`, but in **aiogram 3** this is no longer the case, 
and the correct way is to use built-in filters in the same way as your own, through importing and calling the corresponding classes. 
This is exactly what we see in the second decorator with the call `Command(commands="somecommand")` or briefly: `Command("somecommand")`

All that's left is to import the file with handlers into the entry point and connect the new router to the dispatcher (new lines are highlighted):

```python title="bot.py" hl_lines="5 12"
import asyncio

from aiogram import Bot, Dispatcher

from handlers import group_games


async def main():
    bot = Bot(token="TOKEN")
    dp = Dispatcher()

    dp.include_router(group_games.router)

    # Start the bot and skip all accumulated incoming updates
    # Yes, this method can be called even if you're using polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
```

Let's check:

![Filter working in a group](../images/en/filters-and-middlewares/group_filter.png)

Everything seems good, but what if we have not 2 handlers, but 10? We'll have to specify our 
filter for each one and not forget anywhere. Fortunately, filters can be attached directly to routers! In this case, the check 
will be performed exactly once, when the update reaches that router. This can be useful 
if you're doing various "heavy" tasks in the filter, like accessing the Bot API; otherwise, you can 
easily encounter a floodwait.

Here's our file with handlers for dice in its final form:

```python title="handlers/group_games.py"
from aiogram import Router
from aiogram.enums.dice_emoji import DiceEmoji
from aiogram.filters import Command
from aiogram.types import Message

from filters.chat_type import ChatTypeFilter

router = Router()
router.message.filter(
    ChatTypeFilter(chat_type=["group", "supergroup"])
)


@router.message(Command("dice"))
async def cmd_dice_in_group(message: Message):
    await message.answer_dice(emoji=DiceEmoji.DICE)


@router.message(Command("basketball"))
async def cmd_basketball_in_group(message: Message):
    await message.answer_dice(emoji=DiceEmoji.BASKETBALL)
```

!!! info ""
    Generally speaking, such a filter on chat type can be done a bit differently. Despite the fact 
    that there are four types of chats (private, group, supergroup, channel), the update of type `message` 
    cannot come from channels, as they have their own update `channel_post`. And when we 
    filter groups, usually it doesn't matter whether it's a regular group or a supergroup, as long as it's not a private chat.

    Thus, the filter itself can be reduced to a conditional `ChatTypeFilter(is_group=True/False)`
    and simply check if it's a private chat or not. The specific implementation is left to the reader's discretion.

In addition to True/False, filters can pass something to handlers that have passed the filter. This can be useful 
when we don't want to process a message in the handler because we've already done it in the filter. To make 
this clearer, let's write a filter that will pass a message if it contains usernames, and at the same time 
"push" the found values into handlers.

In the filters directory, we create a new file `find_usernames.py`:

```python title="filters/find_usernames.py" hl_lines="24 26"
from typing import Union, Dict, Any

from aiogram.filters import BaseFilter
from aiogram.types import Message


class HasUsernamesFilter(BaseFilter):
    async def __call__(self, message: Message) -> Union[bool, Dict[str, Any]]:
        # If entities don't exist at all, None will be returned,
        # in this case we consider it an empty list
        entities = message.entities or []

        # Check any usernames and extract them from the text
        # using the extract_from() method. See the chapter
        # about working with messages for more details
        found_usernames = [
            item.extract_from(message.text) for item in entities
            if item.type == "mention"
        ]

        # If there are usernames, then "push" them into the handler
        # with the name "usernames"
        if len(found_usernames) > 0:
            return {"usernames": found_usernames}
        # If we didn't find any username, return False
        return False
```

And we create a new file with a handler:

```python title="handlers/usernames.py" hl_lines="6 13 17 21"
from typing import List

from aiogram import Router, F
from aiogram.types import Message

from filters.find_usernames import HasUsernamesFilter

router = Router()


@router.message(
    F.text,
    HasUsernamesFilter()
)
async def message_with_usernames(
        message: Message,
        usernames: List[str]
):
    await message.reply(
        f'Thanks! I will definitely subscribe to '
        f'{", ".join(usernames)}'
    )
```

In case at least one username is found, the `HasUsernamesFilter` filter will not just return `True`, but 
a dictionary where the extracted usernames will be stored under the key `usernames`. Accordingly, in the handler to which 
this filter is attached, you can add an argument with exactly the same name to the handler function. Voilà! 
Now there's no need to parse the entire message again and extract the list of usernames:

![List the extracted usernames](../images/en/filters-and-middlewares/data_propagation_in_filter.png)

### Magic filters {: id="magic-filters" }

After getting acquainted with `ChatTypeFilter` from the previous section, someone might exclaim: 
"why so complicated, when you can simply use a lambda: 
`lambda m: m.chat.type in ("group", "supergroup")`"? And you're right! Indeed, for some 
simple cases, when you just need to check the value of an object field, creating a separate 
file with a filter, then importing it, doesn't make much sense.

Alex, the founder and lead developer of aiogram, wrote the 
[magic-filter](https://github.com/aiogram/magic-filter/) library, implementing dynamic retrieval 
of object attribute values (kind of like `getattr` on steroids). Moreover, it already comes with **aiogram 3.x**. 
If you've installed "version 3", then you've already installed **magic-filter**.

!!! info ""
    The magic-filter library is also available on [PyPi](https://pypi.org/project/magic-filter/) 
    and can be used separately from aiogram in your other projects. When using the 
    library in aiogram, you will have one additional feature, which we'll discuss 
    later in this chapter.

The capabilities of the "magic filter" are described in quite detail in the
[aiogram documentation](https://docs.aiogram.dev/en/dev-3.x/dispatcher/filters/magic_filters.html), but here 
we'll focus on the main points.

Let's recall what a message's "content type" is. This concept doesn't exist in the Bot API, but it 
exists in both pyTelegramBotAPI and aiogram. The idea is simple: if the `photo` field in a 
[Message](https://core.telegram.org/bots/api#message) object is not empty (i.e., not equal to `None` 
in Python), then this message contains an image, therefore, we consider its 
content type to be `photo`. And the filter `content_types="photo"` will catch only such messages, 
saving the developer from having to check this attribute inside the handler.

Now it's not hard to imagine that a lambda expression that in plain language sounds like 
"the 'photo' attribute of the passed variable 'm' must not be equal to None", in Python looks like 
`lambda m: m.photo is not None`, or, simplifying slightly, `lambda m: m.photo`. And `m` itself becomes 
the object we are filtering. For example, an object of type `Message`.

Magic-filter offers a similar thing. For this, you need to import the `MagicFilter` class from aiogram, 
but we import it not by its full name, but by the single letter alias `F`:

```python
from aiogram import F

# Here F is the message
@router.message(F.photo)
async def photo_msg(message: Message):
    await message.answer("This is definitely some kind of image!")
```

Instead of the old variant `ContentTypesFilter(content_types="photo")`, the new one is `F.photo`. Convenient! And now, 
armed with such sacred knowledge, we can easily replace the `ChatTypeFilter` filter with magic:  
`router.message.filter(F.chat.type.in_({"group", "supergroup"}))`.  
Moreover, even checking content types can be represented as a magic filter:  
`F.content_type.in_({'text', 'sticker', 'photo'})` or `F.photo | F.text | F.sticker`.

Also, it's worth remembering that filters can be applied not only to **Message** processing, but also to any other 
types of updates: callbacks, inline queries, (my_)chat_member, and others.

Let's look at that "exclusive" feature of magic-filter in **aiogram 3.x**. It's about the 
method `as_(<some text>)`, which allows you to get the filter result as a handler argument. Here's a short 
example to clarify: in messages with photos, these images come in an array, which is usually 
sorted in increasing quality order. Accordingly, you can immediately get the photo object 
of the highest quality in the handler:

```python
from aiogram.types import Message, PhotoSize

@router.message(F.photo[-1].as_("largest_photo"))
async def forward_from_channel_handler(message: Message, largest_photo: PhotoSize) -> None:
    print(largest_photo.width, largest_photo.height)
```

A more complex example. If a message is forwarded from anonymous group administrators 
or from some channel, then the `forward_from_chat` field in the `Message` object will be non-empty with an object 
of type `Chat` inside. Here's what an example will look like that will only work if the `forward_from_chat` field 
is not empty, and in the `Chat` object, the `type` field is equal to `channel` (in other words, we filter out forwards from anonymous 
admins, reacting only to forwards from channels):

```python
from aiogram import F
from aiogram.types import Message, Chat

@router.message(F.forward_from_chat[F.type == "channel"].as_("channel"))
async def forwarded_from_channel(message: Message, channel: Chat):
    await message.answer(f"This channel's ID is {channel.id}")
```

An even more complex example. With magic-filter, you can check list elements for compliance with some criteria:

```python
from aiogram.enums import MessageEntityType

@router.message(F.entities[:].type == MessageEntityType.EMAIL)
async def all_emails(message: Message):
    await message.answer("All entities are emails")


@router.message(F.entities[...].type == MessageEntityType.EMAIL)
async def any_emails(message: Message):
    await message.answer("At least one email!")
```

### MagicData {: id="magic-data" }

Finally, let's briefly touch on [MagicData](https://docs.aiogram.dev/en/latest/dispatcher/filters/magic_data.html). This filter 
allows you to move up a level in terms of filters and operate with values that are passed through middlewares or 
into the dispatcher/polling/webhook. Suppose you have a popular bot. And the time has come 
to perform maintenance: back up the database, clean up logs, etc. But at the same time, you don't want to shut down the bot 
to avoid losing a new audience: let it respond to users saying, please wait a bit.

One possible solution is to make a special router that will intercept messages, callbacks, etc., if 
in some way a boolean value `maintenance_mode` equal to `True` is passed to the bot. A simple single-file example for 
understanding this logic is available below:

```python
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import MagicData, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Create a router for maintenance mode and set filters on the types
maintenance_router = Router()
maintenance_router.message.filter(MagicData(F.maintenance_mode.is_(True)))
maintenance_router.callback_query.filter(MagicData(F.maintenance_mode.is_(True)))

regular_router = Router()

# Handlers of this router will intercept all messages and callbacks 
# if maintenance_mode is True
@maintenance_router.message()
async def any_message(message: Message):
    await message.answer("The bot is in maintenance mode. Please wait.")


@maintenance_router.callback_query()
async def any_callback(callback: CallbackQuery):
    await callback.answer(
        text="The bot is in maintenance mode. Please wait",
        show_alert=True
    )

# Handlers of this router are used OUTSIDE maintenance mode,
# i.e. when maintenance_mode is False or not specified at all
@regular_router.message(CommandStart())
async def cmd_start(message: Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="Click me", callback_data="anything")
    await message.answer(
        text="Some text with a button",
        reply_markup=builder.as_markup()
    )


@regular_router.callback_query(F.data == "anything")
async def callback_anything(callback: CallbackQuery):
    await callback.answer(
        text="This is some regular action",
        show_alert=True
    )


async def main() -> None:
    bot = Bot('1234567890:AaBbCcDdEeFfGrOoShAHhIiJjKkLlMmNnOo')
    # In real life, the maintenance_mode value
    # will be taken from an external source (e.g., config or via API)
    # Remember that since bool type is immutable,
    # changing it at runtime won't affect anything
    dp = Dispatcher(maintenance_mode=True)
    # The maintenance router must be first
    dp.include_routers(maintenance_router, regular_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
```

!!! tip "Everything should be in moderation"
    Magic-filter provides a powerful tool for filtering and sometimes allows you to concisely describe complex logic, 
    but it's not a panacea or a universal tool. If you can't immediately write a beautiful magic filter, 
    don't worry; just make a class filter. 
    No one will judge you for that.


## Middlewares {: id="middlewares" }

### Why do we need middlewares? {: id="why-middlewares" }

Imagine you came to a nightclub with some goal (to listen to music, have a cocktail, 
meet new people). And at the entrance, there's a bouncer. He might just let you in, 
he might check your ID and decide whether you'll get in or not, he might give you a paper bracelet 
to later distinguish real guests from accidentally wandered ones, or he might not let you in at all, sending you home.

In aiogram terminology, you are the update, the nightclub is a set of handlers, and the bouncer at the entrance is the middleware. The task of the latter 
is to intervene in the process of handling updates to implement some logic. Going back to the example above, what can you 
do inside middlewares?

* log events;
* pass some objects to handlers (for example, a database session from a session pool);
* substitute update handling, not passing to handlers;
* silently let updates pass as if they never existed;
* ... anything else!

### Types and structure of middlewares {: id="middlewares-structure" }

Let's refer to the aiogram 3.x documentation again, but this time in 
[another section](https://docs.aiogram.dev/en/dev-3.x/dispatcher/middlewares.html#basics) and look at 
the following image:

![middleware "onion"](../images/en/filters-and-middlewares/middlewares_structure.png)

It turns out there are two types of middlewares: outer and inner (or simply "middlewares"). What's the difference? 
Outer ones are executed before filtering begins, and inner ones after. In practice, this means that a message/callback/inline query 
passing through an outer middleware may not reach any handler, but if it reaches an inner one, then there will 
definitely be some handler next.

!!! info "Middlewares on Update type"
    It's worth reminding that Update is the general type for all kinds of events in Telegram. And there are two important features about them 
    in terms of their processing by aiogram:  
    • Inner middleware on Update is called **always** (i.e., in this case, there's no difference between Outer and Inner).  
    • Middlewares on Update can only be hung on the dispatcher (root router).

Let's consider the simplest middleware:

```python linenums="1"
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

class SomeMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        print("Before handler")
        result = await handler(event, data)
        print("After handler")
        return result
```

Each middleware built on classes (we won't consider 
[other variants](https://docs.aiogram.dev/en/dev-3.x/dispatcher/middlewares.html#function-based)) must implement 
the `__call__()` method with three arguments:

1. **handler** — actually, the handler object that will be executed. It only makes sense for inner middlewares, 
   since the outer middleware doesn't yet know which handler the update will go into.
2. **event** — the type of Telegram object we're processing. Usually it's Update, Message, CallbackQuery or InlineQuery 
   (but not only). If you know exactly what types of objects you're processing, feel free to write, for example, `Message` instead of 
   `TelegramObject`.
3. **data** — data associated with the current update: FSM, additional fields passed from filters, flags (more on them later), etc. 
   Into this same `data`, we can put some of our own data from middlewares, which will be available as 
   arguments in handlers (just like in filters).

With the function body, it gets even more interesting.

* Everything you write BEFORE line 13 will be executed before passing control 
  to the underlying handler (which could be another middleware or directly the handler).
* Everything you write AFTER line 13 will be executed after exiting the underlying handler.
* If you want the processing to continue, you **MUST** call `await handler(event, data)`. If you want to 
  "drop" the update, just don't call it.
* If you don't need to get data from the handler, then put 
  `return await handler(event, data)` as the last line of the function. If you don't return `await handler(event, data)` (implicit `return None`), 
  then the update will be considered "dropped".

All our familiar objects (`Message`, `CallbackQuery`, etc.) are updates (`Update`), so for `Message`, first 
middlewares for `Update` will be executed, and only then for the `Message` itself. Let's keep our `print()` statements from the example above and 
trace how the middlewares will be executed if we register one outer and one inner middleware for the types 
`Update` and `Message`.

If a message (`Message`) is eventually processed by some handler:

1. `[Update Outer] Before handler`
2. `[Update Inner] Before handler`
3. `[Message Outer] Before handler`
4. `[Message Inner] Before handler`
5. `[Message Inner] After handler`
6. `[Message Outer] After handler`
7. `[Update Inner] After handler`
8. `[Update Outer] After handler`

If the message doesn't find the right handler:

1. `[Update Outer] Before handler`
2. `[Update Inner] Before handler`
3. `[Message Outer] Before handler`
4. `[Message Outer] After handler`
5. `[Update Inner] After handler`
6. `[Update Outer] After handler`

!!! question "Banning users in the bot"
    Very often in Telegram bot groups, the same question is asked: "how to ban a user in the bot so that 
    they can't write to the bot?". Most likely, the best place for this would be an outer middleware on Update, as the earliest 
    stage of processing a user's request. Moreover, one of the built-in aiogram middlewares puts a dictionary 
    with user information in `data` under the key `event_from_user`. You can then retrieve the user ID from there, compare it with 
    some of your "blacklist" and simply do `return` to prevent further processing 
    down the chain.

### Examples of middlewares {: id="middlewares-examples" }

Let's consider several examples of middlewares.

#### Passing arguments to middleware {: id="middleware-pass-arguments" }

We're using middleware classes, so they have a constructor. This allows us to customize the behavior of the code inside, 
controlling it from outside. For example, from a configuration file. Let's write a useless but illustrative "slowing down" middleware 
that will slow down the processing of incoming messages by the specified number of seconds:

```python hl_lines="7 8 18"
import asyncio
from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

class SlowpokeMiddleware(BaseMiddleware):
    def __init__(self, sleep_sec: int):
        self.sleep_sec = sleep_sec

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        # Wait for the specified number of seconds and pass control further down the chain
        # (this can be either a handler or the next middleware)
        await asyncio.sleep(self.sleep_sec)
        result = await handler(event, data)
        # If you return something in the handler, that value will end up in result
        print(f"Handler was delayed by {self.sleep_sec} seconds")
        return result
```

And now let's hang it on two routers with different values:

```python
from aiogram import Router
from <...> import SlowpokeMiddleware

# Somewhere else
router1 = Router()
router2 = Router()

router1.message.middleware(SlowpokeMiddleware(sleep_sec=5))
router2.message.middleware(SlowpokeMiddleware(sleep_sec=10))
```

#### Passing data from middleware {: id="middleware-store-data" }

As we already found out earlier, when processing the next update, middlewares have access to a `data` dictionary 
that contains various useful objects: bot, the author of the update (event_from_user), etc. But we can also fill this 
dictionary with anything we want. Moreover, later-called middlewares can see what earlier-called ones put there.

Consider the following situation: the first middleware gets some internal ID by the user's Telegram ID (for example, from 
a supposedly third-party service), and the second middleware calculates the user's "lucky month" based on this internal ID
(the remainder when dividing the internal ID by 12). All of this is placed in the handler, which either delights or disappoints the person who called 
the command. It sounds complicated, but you'll understand everything now. Let's start with the middlewares:

```python hl_lines="20 21 32 33 36 37"
from random import randint
from typing import Any, Callable, Dict, Awaitable
from datetime import datetime
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

# Middleware that gets the user's internal ID from some third-party service
class UserInternalIdMiddleware(BaseMiddleware):
    # Of course, we don't have any service in our example,
    # just harsh random:
    def get_internal_id(self, user_id: int) -> int:
        return randint(100_000_000, 900_000_000) + user_id

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user = data["event_from_user"]
        data["internal_id"] = self.get_internal_id(user.id)
        return await handler(event, data)

# Middleware that calculates the user's "lucky month"
class HappyMonthMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        # Get value from the previous middleware
        internal_id: int = data["internal_id"]
        current_month: int = datetime.now().month
        is_happy_month: bool = (internal_id % 12) == current_month
        # Put True or False into data to retrieve it in the handler
        data["is_happy_month"] = is_happy_month
        return await handler(event, data)
```

Now let's write a handler, put it in a router, and attach the router to the dispatcher. We'll hang the first middleware as outer on the dispatcher, 
because (according to the plan) this internal ID is needed always and everywhere. And we'll hang the second middleware as inner on the specific router, 
since the calculation of the lucky month is only needed there.

```python hl_lines="4 5"
@router.message(Command("happymonth"))
async def cmd_happymonth(
        message: Message, 
        internal_id: int, 
        is_happy_month: bool
):
    phrases = [f"Your ID in our service: {internal_id}"]
    if is_happy_month:
        phrases.append("This is your lucky month!")
    else:
        phrases.append("Be more careful this month...")
    await message.answer(". ".join(phrases))

# Somewhere else:
async def main():
    dp = Dispatcher()
    # <...>
    dp.update.outer_middleware(UserInternalIdMiddleware())
    router.message.middleware(HappyMonthMiddleware())
```

Here are the results we got in November (11th month):

![Someone's month is lucky, someone's not so much](../images/en/filters-and-middlewares/happymonth.png)

#### No callbacks on weekends! {: id="no-callbacks-on-weekend" }

Imagine a factory has a Telegram bot, and every morning the factory workers must press an inline button 
to confirm their presence and capability. The factory works 5/2 and we want the clicks not to be registered 
on Saturdays and Sundays. Since pressing the button is tied to complex logic (sending data to the access control system), on weekends we'll 
simply "drop" the update and display an error window. The following example can be copied in its entirety and run:

```python
import asyncio
import logging
import sys
from datetime import datetime
from typing import Any, Callable, Dict, Awaitable

from aiogram import Bot, Dispatcher, Router, BaseMiddleware, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

# This will be an outer middleware for any callbacks
class WeekendCallbackMiddleware(BaseMiddleware):
    def is_weekend(self) -> bool:
        # 5 - Saturday, 6 - Sunday
        return datetime.utcnow().weekday() in (5, 6)

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        # You can safeguard and ignore the middleware
        # if it's set up by mistake NOT on callbacks
        if not isinstance(event, CallbackQuery):
            # log it somehow
            return await handler(event, data)

        # If today is not Saturday or Sunday,
        # then continue processing.
        if not self.is_weekend():
            return await handler(event, data)
        # Otherwise, respond to the callback ourselves
        # and stop further processing
        await event.answer(
            "What work? The factory is closed until Monday!",
            show_alert=True
        )
        return


@router.message(Command("checkin"))
async def cmd_checkin(message: Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="I'm at work!", callback_data="checkin")
    await message.answer(
        text="Press this button only on weekdays!",
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data == "checkin")
async def callback_checkin(callback: CallbackQuery):
    # Lots of complex code here
    await callback.answer(
        text="Thank you for confirming your presence!",
        show_alert=True
    )


async def main() -> None:
    bot = Bot('1234567890:AaBbCcDdEeFfGrOoShAHhIiJjKkLlMmNnOo')
    dp = Dispatcher()
    dp.callback_query.outer_middleware(WeekendCallbackMiddleware())
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
```

Now, if we play a bit with time travel, we can see that on weekdays the bot responds normally, 
and on weekends it displays an error.

### Flags {: id="flags" }

Another interesting feature of **aiogram 3.x** is [flags](https://docs.aiogram.dev/en/dev-3.x/dispatcher/flags.html). Essentially, 
these are certain "markers" of handlers that can be read in middlewares and elsewhere. With flags, you can mark handlers 
without messing with their internal structure, to then do something in middlewares, for example, throttling.

Let's consider a slightly modified code 
[from the documentation](https://docs.aiogram.dev/en/dev-3.x/dispatcher/flags.html#example-in-middlewares). Suppose 
your bot has many handlers that deal with sending media files or preparing text for subsequent 
sending. If such actions take a long time, it's considered good practice to show a "typing" or 
"sending a photo" status using the [sendChatAction](https://core.telegram.org/bots/api#sendchataction) method. 
By default, such an event is sent for only 5 seconds, but will automatically end if the message 
is sent earlier. aiogram has a helper class `ChatActionSender` that allows you to send 
the selected status until the message is sent.

We also don't want to stuff `ChatActionSender` work inside each handler; let the middleware do that with those 
handlers that have the `long_operation` flag set with the status value (for example, `typing`, `choose_sticker`...). 
Here's the middleware itself:

```python
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender


class ChatActionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        long_operation_type = get_flag(data, "long_operation")

        # If there's no such flag on the handler
        if not long_operation_type:
            return await handler(event, data)

        # If the flag exists
        async with ChatActionSender(
                action=long_operation_type,
                chat_id=event.chat.id,
                bot=data["bot"],
        ):
            return await handler(event, data)
```

Accordingly, for the flag to be read, it must be specified somewhere. 
Option: `@dp.message(<your filters here>, flags={"long_operation": "upload_video_note"})`


!!! info ""
    An example of a throttling middleware can be seen in my 
    [casino bot](https://github.com/MasterGroosha/telegram-casino-bot/blob/09ef66cd9d1ff4709791126b058c7313c71c99c5/bot/middlewares/throttling.py).
