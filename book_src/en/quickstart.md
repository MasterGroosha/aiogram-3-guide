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

