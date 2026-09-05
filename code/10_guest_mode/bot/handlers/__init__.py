from aiogram import Router

from . import (
    guest_mode,
)


def get_routers() -> list[Router]:
    return [
        guest_mode.router,
    ]

