import asyncio
from random import randint

import structlog
from aiogram import F, Router, Bot
from aiogram.filters import StateFilter
from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import Message
from structlog.typing import FilteringBoundLogger

from bot.prompts import prompts
from bot.llm import LLMClient
from bot.storage import Message as LLMMessage
from bot.storage import memory_chat_storage, Role
from bot.text_utils import trim_text_smart

from bot.states import NewChatFlow

router = Router()
logger: FilteringBoundLogger = structlog.get_logger()


async def update_topic_title(
        llm_client: LLMClient,
        message: Message,
        bot: Bot,
):
    print("called update topic title")
    title: str | None = await llm_client.generate_topic_title(message.text)
    print("title", title)
    if title:
        try:
            await bot.edit_forum_topic(
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                name=title
            )
        except Exception:
            await logger.aexception(
                "Failed to rename topic",
            )


@router.message(
    F.text,
    NewChatFlow.choosing_persona,
)
async def handle_text_before_persona_select(
        message: Message,
):
    try:
        await message.delete()
    except:
        await logger.aexception(
            "Failed to delete persona select message",
        )



@router.message(
    F.text,
    StateFilter("*"),
)
async def handle_message(
        message: Message,
        llm_client: LLMClient,
        bot: Bot,
):
    llm_chat = await memory_chat_storage.get(
        user_id=message.from_user.id,
        thread_id=message.message_thread_id,
    )
    if llm_chat is None:
        await message.answer(
            "Не удалось получить историю сообщений. "
            "Пожалуйста, создайте новый топик-чат: вернитесь в основной раздел и вызовите команду /new"
        )
        return

    # Совет: если вы хотите использовать заглушки в промте,
    # например, для подстановки текущей даты,
    # то это можно сделать где-то тут при создании
    # словаря с системным промтом.
    prompt = {
        "role": "system",
        "content": prompts[llm_chat.meta.prompt_key]["prompt"],
    }

    # Получаем всю предыдущую историю
    chat_history = [item.to_call_dict() for item in llm_chat.messages]

    # Сверху кладём свежее сообщение юзера
    chat_history.append({"role": "user", "content": message.text})

    text = ""
    safe_text = ""
    retry_backoff = 0.0
    update_interval = 0.7
    last_update = 0.0
    draft_id = randint(1, 100_000_000)
    async for delta in await llm_client.generate_response(
        messages=[prompt] + chat_history,
        stream=True,
        temperature=llm_chat.meta.temperature,
    ):
        text += delta
        safe_text = trim_text_smart(text)
        now = asyncio.get_running_loop().time()
        if now - last_update < update_interval + retry_backoff:
            if safe_text != text:
                break
            await logger.adebug("Skipping updating draft; still merging chunks")
            continue
        await logger.adebug("Enough time passed, updating draft")
        try:
            await bot.send_message_draft(
                draft_id=draft_id,
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                text=safe_text,
            )
            last_update = now
        except TelegramRetryAfter as ex:
            retry_backoff += 0.1
            last_update = now
            await logger.awarning(
                f"Streaming rate limit, need to wait {ex.retry_after} sec",
            )
            await asyncio.sleep(ex.retry_after)
        except Exception:
            await logger.aexception("Failed to stream message draft")
            return

        if safe_text != text:
            break

    await message.answer(safe_text)

    # Сверху кладём свежий ответ от LLM
    chat_history.append(
        {
            "role": Role.ASSISTANT.value,
            "content": safe_text,
        }
    )
    # Формируем Pydantic-объекты и записываем в llm_chat
    llm_chat.messages = [
        LLMMessage.from_call_dict(item)
        for item in chat_history
    ]
    # Замещаем старый llm_chat новым
    await memory_chat_storage.update(
        user_id=message.from_user.id,
        thread_id=message.message_thread_id,
        new_version=llm_chat,
    )
    # Просто для удобства, чтобы убедиться,
    # что история пишется и читается целиком
    await logger.adebug(
        f"Chat history now has {len(llm_chat.messages)} msg(s)",
    )

    # Если это самое начало топика-чата,
    # то генерируем название.
    print(f"{llm_chat.is_chat_start=}")
    if llm_chat.is_chat_start:
        asyncio.create_task(update_topic_title(
            llm_client=llm_client,
            message=message,
            bot=bot,
        ))