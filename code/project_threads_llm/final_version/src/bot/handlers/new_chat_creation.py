import structlog
from aiogram import Router, Bot
from aiogram.enums.topic_icon_color import TopicIconColor
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message
from structlog.typing import FilteringBoundLogger

from bot.keyboards import make_prompt_keyboard
from bot.states import NewChatFlow
from bot.storage import memory_chat_storage

router = Router()
logger: FilteringBoundLogger = structlog.get_logger()


@router.message(Command("new"))
async def cmd_start(
        message: Message,
        bot: Bot,
        state: FSMContext,
):
    try:
        new_topic = await bot.create_forum_topic(
            chat_id=message.chat.id,
            name="Новый чат",
            icon_color=TopicIconColor.YELLOW,
        )
    except:  # noqa
        await logger.aexception("Failed to create new topic")
        await message.answer("Что-то пошло не так. Пожалуйста, попробуйте ещё раз.")
        return

    new_topic_id = new_topic.message_thread_id
    await memory_chat_storage.create(
        user_id=message.from_user.id,
        thread_id=new_topic_id,
    )

    key = StorageKey(
        bot_id=bot.id,
        chat_id=message.chat.id,
        user_id=message.from_user.id,
        thread_id=new_topic_id,
    )
    fsm = FSMContext(
        storage=state.storage,
        key=key,
    )
    await bot.send_message(
        chat_id=message.chat.id,
        text="Пожалуйста, выберите стиль для этого чата одной из кнопок ниже.",
        message_thread_id=new_topic_id,
        reply_markup=make_prompt_keyboard(),
    )
    await fsm.set_state(NewChatFlow.choosing_persona)