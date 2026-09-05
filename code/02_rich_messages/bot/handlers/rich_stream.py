import asyncio
from random import randint

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import InputRichMessage, Message, MessageGenerationStopped

router = Router(name="rich_stream")

# Финальный текст, который мы будем «печатать» по кусочкам.
FINAL_MARKDOWN = """\
# Что такое стриминг черновика

Метод `sendRichMessageDraft` показывает пользователю **временное превью**
сообщения, пока оно ещё генерируется — ровно так ведут себя нейросетевые
ассистенты, печатающие ответ постепенно.

## Как это работает

- Черновик **эфемерный**: он живёт около 30 секунд и сам исчезает.
- Все апдейты с одним и тем же `draft_id` Telegram анимирует как плавную правку.
- Чтобы сообщение осталось в чате насовсем, в конце нужно отправить его
  обычным `sendRichMessage`.
"""


def _build_chunks(text: str) -> list[str]:
    """
    Режем итоговый текст на нарастающие префиксы.
    В реальном боте на их месте были бы токены от LLM, которые вы
    накапливаете в буфер и периодически отправляете черновиком.
    """
    words = text.split(" ")
    chunks: list[str] = []
    step = 12  # отправляем превью примерно раз в 12 слов, чтобы не упереться в лимиты
    for i in range(step, len(words), step):
        chunks.append(" ".join(words[:i]))
    chunks.append(text)  # последний кусок — полный текст
    return chunks


@router.message(Command("sendrichstream"))
async def cmd_send_rich_stream(
        message: Message,
        bot: Bot,
) -> None:
    # Генерируем случайный айди черновика
    draft_id = randint(1, 100_000_000)

    # Имитируем первичную задержку перед «первым токеном»:
    # покажем заглушку для пустого текста и выждем паузу в 2 секунды.
    await bot.send_rich_message_draft(
        chat_id=message.chat.id,
        draft_id=draft_id,
        rich_message=InputRichMessage(markdown="<tg-thinking>Думаю...</tg-thinking>"),
    )
    await asyncio.sleep(2.0)

    for chunk in _build_chunks(FINAL_MARKDOWN):
        await bot.send_rich_message_draft(
            chat_id=message.chat.id,
            draft_id=draft_id,
            rich_message=InputRichMessage(markdown=chunk),
        )
        await asyncio.sleep(0.7)

    # Превью само растворится, поэтому фиксируем результат настоящим сообщением.
    await message.answer_rich(
        rich_message=InputRichMessage(markdown=FINAL_MARKDOWN),
    )


# Черновики, которые пользователь может остановить: draft_id -> «стоп-сигнал»
active_drafts: dict[int, asyncio.Event] = {}                      # [1]


@router.message(Command("sendrichstreamstop"))
async def cmd_send_rich_stream_stop(
        message: Message,
        bot: Bot,
) -> None:
    draft_id = randint(1, 100_000_000)
    stop_event = asyncio.Event()
    active_drafts[draft_id] = stop_event

    # Если пользователь ничего не нажмёт, отправим полный текст
    text = FINAL_MARKDOWN
    try:
        for chunk in _build_chunks(FINAL_MARKDOWN):
            await bot.send_rich_message_draft(
                chat_id=message.chat.id,
                draft_id=draft_id,
                rich_message=InputRichMessage(markdown=chunk),
                can_stop=True,                                    # [2]
                keep_on_stop=True,                                # [3]
            )
            await asyncio.sleep(0.7)
            if stop_event.is_set():                               # [4]
                text = chunk
                break
    finally:
        active_drafts.pop(draft_id, None)                         # [5]

    await message.answer_rich(                                    # [6]
        rich_message=InputRichMessage(markdown=text),
    )


@router.stopped_message_generation()                              # [7]
async def on_generation_stopped(
        event: MessageGenerationStopped,
) -> None:
    stop_event = active_drafts.get(event.draft_id)
    if stop_event is not None:
        stop_event.set()
