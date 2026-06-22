from aiogram import Router

from . import (
    start,
    rich_send,
    rich_stream,
    rich_media,
    rich_parse,
)


def get_routers() -> list[Router]:
    return [
        start.router,
        rich_send.router,
        rich_stream.router,
        rich_media.router,
        # rich_parse идёт последним: его фильтр срабатывает на любое
        # входящее Rich Message, не перехватывая команды выше.
        rich_parse.router,
    ]
