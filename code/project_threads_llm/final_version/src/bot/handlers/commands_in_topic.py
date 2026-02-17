import structlog
from aiogram import Router, Bot
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from structlog.typing import FilteringBoundLogger

router = Router()
logger: FilteringBoundLogger = structlog.get_logger()


@router.message(Command("rename_topic"))
async def cmd_rename_topic(
        message: Message,
        command: CommandObject,
        bot: Bot,
):
    if command.args is None:
        await message.answer(
            "Ошибка. Вы должны указать новое название топика через пробел.\n"
            "Например: /rename_topic Новый топик"
        )
        return
    new_topic_name = command.args
    try:
        await bot.edit_forum_topic(
            chat_id=message.chat.id,
            message_thread_id=message.message_thread_id,
            name=new_topic_name,
        )
    except:  # noqa
        await message.answer(
            "Ошибка. Не удалось изменить название топика. Пожалуйста, попробуйте ещё раз."
        )
        await logger.aexception(
            "Failed to rename topic",
            new_name=new_topic_name,
        )


@router.message(Command("favorite"))
async def cmd_favorite(
        message: Message,
        bot: Bot,
):
    try:
        await bot.edit_forum_topic(
            chat_id=message.chat.id,
            message_thread_id=message.message_thread_id,
            icon_custom_emoji_id="5235579393115438657",
        )
    except:  # noqa
        await message.answer(
            "Ошибка. Не удалось пометить топик как избранное. Пожалуйста, попробуйте ещё раз."
        )
        await logger.aexception(
            "Failed to mark topic as favorite",
        )
