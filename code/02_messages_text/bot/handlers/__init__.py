from aiogram import Router

from . import (
    start,
    formatting,
    escaping,
    entities,
    keep_formatting,
    commands_args,
    deeplinks,
    link_previews,
    hidden_link,
)


def get_routers() -> list[Router]:
    return [
        start.router,
        formatting.router,
        escaping.router,
        commands_args.router,
        deeplinks.router,
        link_previews.router,
        hidden_link.router,
        # entities идёт перед keep_formatting: оба реагируют на F.text,
        # а срабатывает только первый подходящий роутер по порядку.
        entities.router,
        keep_formatting.router,
    ]
