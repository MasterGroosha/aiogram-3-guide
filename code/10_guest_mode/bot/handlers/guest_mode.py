from datetime import datetime

import structlog
from openai import AsyncOpenAI
from structlog.typing import FilteringBoundLogger

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.types import Message, InlineQueryResultArticle, InputTextMessageContent

router = Router(name="guest_mode")
logger: FilteringBoundLogger = structlog.get_logger()

async def get_llm_response(
        client: AsyncOpenAI,
        prompt: str,
        model: str,
) -> str | None:
    completion = await client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
        ],
        stream=False,
        extra_body={"reasoning": {"enabled": True}},
    )
    if not completion.choices:
        return None
    return completion.choices[0].message.content


@router.guest_message(F.text)
async def guest_message(
        message: Message,
        llm_client: AsyncOpenAI,
        llm_model: str,
        system_prompt: str,
) -> None:
    # Проверка, является ли вызывающее сообщение ответом на какое-то другое.
    if (replied_message := message.reply_to_message) is None:
        # Это пойдет в системный промпт
        replied_message = "(none provided)"
    else:
        replied_message = (
            replied_message.text
            or f"(some mediafile, contents unknown, "
               f"but there is a caption: {replied_message.caption})"
            # Считаем, что не умеем "читать" медиафайлы
            or "(some mediafile, contents unknown)"
        )

    # Подготовка системного промта
    prompt = (
        system_prompt
        .replace("{{replied_message}}", replied_message)
        .replace("{{current_message}}", message.text)  # noqa
        .replace("{{date_today}}", datetime.now().strftime("%d.%m.%Y"))
    )

    await logger.adebug("Making request to an LLM provider")
    response_text = await get_llm_response(
        client=llm_client,
        prompt=prompt,
        model=llm_model,
    )

    await logger.adebug(
        "Received response from an LLM provider",
        response=response_text,
    )
    parse_mode = None
    # Бывает, что ответа от модели нет. В таком случае, пусть будет заглушка.
    if response_text is None:
        response_text = "<i>К сожалению, не удалось получить ответ от модели.</i>"
        parse_mode = ParseMode.HTML

    # Отвечаем на исходный запрос
    await message.answer_guest_query(
        result=InlineQueryResultArticle(
            id="1",
            title=".",
            input_message_content=InputTextMessageContent(
                message_text=response_text,
                parse_mode=parse_mode,
            ),
        )
    )
