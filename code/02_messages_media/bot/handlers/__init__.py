from aiogram import Router

from . import (
    start,
    file_upload,
    file_download,
    albums,
    service_messages,
)


def get_routers() -> list[Router]:
    return [
        start.router,
        file_upload.router,
        file_download.router,
        albums.router,
        service_messages.router,
    ]
