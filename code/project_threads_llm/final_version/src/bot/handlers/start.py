import structlog
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from structlog.typing import FilteringBoundLogger

router = Router()
logger: FilteringBoundLogger = structlog.get_logger()


@router.message(CommandStart())
async def cmd_start(
        message: Message,
):
    await message.answer("Добро пожаловать! Нажмите /new для создания нового чата")