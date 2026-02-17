from aiogram import Router, F

from . import (
    chat_in_general_topic,
    chat_in_topic,
    commands_in_topic,
    in_topic_persona_choose,
    new_chat_creation,
    start,
)

general_topic_router = Router()
general_topic_router.message.filter(F.message_thread_id.is_(None))
general_topic_router.include_routers(
    start.router,
    new_chat_creation.router,
    chat_in_general_topic.router,
)

in_topic_router = Router()
in_topic_router.include_routers(
    in_topic_persona_choose.router,
    commands_in_topic.router,
    chat_in_topic.router,
)


def get_routers() -> list[Router]:
    return [
        general_topic_router,
        in_topic_router,
    ]
