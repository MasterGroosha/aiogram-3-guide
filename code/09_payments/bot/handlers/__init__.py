from aiogram import Router

from . import donate


def get_routers() -> list[Router]:
    return [
        donate.router
    ]

