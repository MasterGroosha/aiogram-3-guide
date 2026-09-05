from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    CopyTextButton,
    DisabledButton,
    InputRichBlockButtons,
    InputRichBlockParagraph,
    InputRichBlockSectionHeading,
    InputRichMessage,
    Message,
    RichMessageButton,
    RichTextButton,
)

router = Router(name="rich_buttons")

RELEASE = "v4.2.0"


def build_release_card() -> InputRichMessage:
    return InputRichMessage(blocks=[
        InputRichBlockSectionHeading(text=f"Релиз {RELEASE}", size=1),
        InputRichBlockParagraph(text=[
            "Тесты зелёные, чейнджлог написан, на часах пятница, 17:45.",
            " Номер релиза можно ",
            RichTextButton(button=RichMessageButton(               # [1]
                text="скопировать одним касанием",
                copy_text=CopyTextButton(text=RELEASE),
            )),
            ", а решение принять кнопками ниже.",
        ]),
        InputRichBlockButtons(                                     # [2]
            buttons=[
                RichMessageButton(
                    text="Катить в прод",
                    style="danger",
                    callback_data="release:deploy",
                ),
                RichMessageButton(
                    text="До понедельника",
                    style="success",
                    callback_data="release:postpone",
                ),
            ],
            align="center",                                        # [3]
        ),
        InputRichBlockButtons(
            buttons=[
                RichMessageButton(
                    text="Чейнджлог",
                    style="primary",
                    url="https://github.com/aiogram/aiogram/releases",
                ),
                RichMessageButton(
                    text="Что вообще происходит?",
                    style="link",                                  # [4]
                    callback_data="release:help",
                ),
                RichMessageButton(
                    text="Откатить",
                    disabled=DisabledButton(),                     # [5]
                ),
            ],
            align="left",
        ),
    ])


@router.message(Command("sendrichbuttons"))
async def cmd_send_rich_buttons(
        message: Message,
) -> None:
    await message.answer_rich(
        rich_message=build_release_card(),
    )


@router.callback_query(F.data.startswith("release:"))              # [6]
async def on_release_button(
        callback: CallbackQuery,
) -> None:
    answers = {
        "release:deploy": "Смелость города берёт. Дежурный предупреждён.",
        "release:postpone": "Мудрое решение. Хороших выходных!",
        "release:help": "Обычный CallbackQuery и обычный F.data, ничего нового.",
    }
    await callback.answer(answers[callback.data], show_alert=True)
