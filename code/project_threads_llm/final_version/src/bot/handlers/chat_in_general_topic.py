import structlog
from aiogram import F, Router
from aiogram.types import Message
from structlog.typing import FilteringBoundLogger

router = Router()
logger: FilteringBoundLogger = structlog.get_logger()


@router.message(F.text)
async def text_message_in_general_topic(
        message: Message,
):
    await message.answer(
        "Сообщения вне топиков-чатов не поддерживаются. "
        "Пожалуйста, создайте новый топик-чат при помощи команды /new."
    )



@router.message(~F.text)
async def nontext_message_in_general_topic(
        message: Message,
):
    await message.answer(
        "В настоящий момент медиафайлы не поддерживаются"
    )
