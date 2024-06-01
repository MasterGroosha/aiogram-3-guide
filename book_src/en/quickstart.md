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

