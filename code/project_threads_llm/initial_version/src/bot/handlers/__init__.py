from aiogram import Router

from . import start


def get_routers() -> list[Router]:
    return [
        start.router
    ]

