from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputRichBlockList,
    InputRichBlockListItem,
    InputRichBlockParagraph,
    InputRichBlockSectionHeading,
    InputRichMessage,
    Message,
    RichTextBold,
)

router = Router(name="rich_edit_blocks")

TASKS = [
    "Прогнать тесты",
    "Обновить документацию",
    "Задеплоить бота",
]


def build_checklist(done: int) -> InputRichMessage:
    """
    Собирает чек-лист с указанным числом выполненных пунктов.
    Вместо двух копипастных строковых констант — одна функция от состояния.
    """
    progress = ["Прогресс: ", RichTextBold(text=f"{done} из {len(TASKS)}")]
    if done >= len(TASKS):
        progress.append(" 🎉")

    return InputRichMessage(blocks=[
        InputRichBlockSectionHeading(text="Чек-лист релиза", size=1),
        InputRichBlockParagraph(text=progress),
        InputRichBlockList(items=[
            InputRichBlockListItem(
                # blocks, а не text: пункт списка — это список блоков
                blocks=[InputRichBlockParagraph(text=task)],
                has_checkbox=True,
                is_checked=index < done,
            )
            for index, task in enumerate(TASKS)
        ]),
    ])


def build_keyboard(done: int) -> InlineKeyboardMarkup | None:
    # Все пункты выполнены — кнопка больше не нужна
    if done >= len(TASKS):
        return None
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="Выполнить следующий пункт",
            # Текущий прогресс кладём прямо в callback_data
            callback_data=f"checklist:{done + 1}",
        )
    ]])


@router.message(Command("sendricheditblocks"))
async def cmd_send_rich_edit_blocks(
        message: Message,
) -> None:
    await message.answer_rich(
        rich_message=build_checklist(0),
        reply_markup=build_keyboard(0),
    )


@router.callback_query(F.data.startswith("checklist:"))
async def on_checklist_step(
        callback: CallbackQuery,
) -> None:
    done = int(callback.data.split(":")[1])
    # Перегенерировать сообщение под новое состояние — одна строка
    await callback.message.edit_text(
        rich_message=build_checklist(done),
        reply_markup=build_keyboard(done),
    )
    await callback.answer()
