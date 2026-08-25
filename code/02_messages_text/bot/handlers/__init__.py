from aiogram import Router

from . import (
    advanced_formatting,
    basic_formatting,
    commands_args,
    commands_prefixes,
    date_and_time,
    deeplinks,
    entities,
    escaping,
    hidden_links,
    keep_formatting,
    link_previews,
    sending_messages,
    start,
)


def get_routers() -> list[Router]:
    return [
        start.router,
        sending_messages.router,
        advanced_formatting.router,
        deeplinks.router,
        date_and_time.router,
        basic_formatting.router,
        escaping.router,
        commands_args.router,
        commands_prefixes.router,
        link_previews.router,
        hidden_links.router,
        # entities идёт перед keep_formatting: оба реагируют на F.text,
        # а срабатывает только первый подходящий роутер по порядку.
        entities.router,
        keep_formatting.router,
    ]
