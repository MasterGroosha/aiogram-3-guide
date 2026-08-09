from aiogram import Router

from . import (
    date_and_time,
    start,
    formatting,
    escaping,
    entities,
    keep_formatting,
    commands_args,
    commands_prefixes,
    deeplinks,
    link_previews,
    hidden_link,
)


def get_routers() -> list[Router]:
    return [
        start.router,
        deeplinks.router,
        date_and_time.router,
        formatting.router,
        escaping.router,
        commands_args.router,
        commands_prefixes.router,
        link_previews.router,
        hidden_link.router,
        # entities идёт перед keep_formatting: оба реагируют на F.text,
        # а срабатывает только первый подходящий роутер по порядку.
        entities.router,
        keep_formatting.router,
    ]
