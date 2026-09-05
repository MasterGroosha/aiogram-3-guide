from aiogram import Router
from aiogram.filters import Command
from aiogram.types import (
    InputRichBlockBlockQuotation,
    InputRichBlockDivider,
    InputRichBlockFooter,
    InputRichBlockMathematicalExpression,
    InputRichBlockParagraph,
    InputRichBlockSectionHeading,
    InputRichBlockTable,
    InputRichMessage,
    Message,
    RichBlockTableCell,
    RichTextAnchor,
    RichTextAnchorLink,
    RichTextBold,
    RichTextCode,
    RichTextItalic,
    RichTextSpoiler,
    RichTextSuperscript,
)

router = Router(name="rich_blocks")

# Данные для таблицы: (метрика, было, стало)
METRICS = [
    ("MRR", "$35k", "$42k"),
    ("Активные чаты", "1 240", "1 510"),
    ("Отвалившиеся боты", "12", "7"),
]


def build_metrics_table() -> InputRichBlockTable:
    """
    Собирает таблицу метрик циклом по данным.
    Ровно то, ради чего блоки и нужны: никакой конкатенации строк с <tr>.
    """
    # align и valign у RichBlockTableCell — обязательные поля, без дефолтов
    header = [
        RichBlockTableCell(text="Метрика", align="left", valign="middle", is_header=True),
        RichBlockTableCell(text="Было", align="right", valign="middle", is_header=True),
        RichBlockTableCell(text="Стало", align="right", valign="middle", is_header=True),
    ]
    rows = [
        [
            RichBlockTableCell(text=name, align="left", valign="middle"),
            RichBlockTableCell(text=before, align="right", valign="middle"),
            RichBlockTableCell(text=after, align="right", valign="middle"),
        ]
        for name, before, after in METRICS
    ]
    return InputRichBlockTable(
        cells=[header, *rows],
        is_bordered=True,
        is_striped=True,
        is_compact=True,
    )


def build_report() -> InputRichMessage:
    return InputRichMessage(blocks=[
        # size=1 — самый крупный заголовок, аналог <h1>
        InputRichBlockSectionHeading(text="Отчёт за квартал", size=1),
        InputRichBlockParagraph(text=[
            "Тот же самый отчёт, что и в ",
            RichTextCode(text="/sendrich"),
            ", но собранный из ",
            RichTextBold(text="блоков"),
            " — без единого тега и без экранирования",
            # Сноска: якорь-точка возврата и ссылка на текст сноски в футере
            RichTextSuperscript(text=[
                RichTextAnchor(name="ref-1"),
                RichTextAnchorLink(text="1", anchor_name="note-1"),
            ]),
            ".",
        ]),
        InputRichBlockSectionHeading(text="Ключевые метрики", size=2),
        build_metrics_table(),
        InputRichBlockSectionHeading(text="Немного математики", size=2),
        InputRichBlockParagraph(text="Прирост считаем по простой формуле:"),
        InputRichBlockMathematicalExpression(
            expression="rate = (new - old) / old",
        ),
        InputRichBlockBlockQuotation(
            blocks=[
                InputRichBlockParagraph(text=[
                    "Это блочная цитата. Внутри неё можно держать ",
                    RichTextItalic(text="курсив"),
                    ", ",
                    RichTextCode(text="код"),
                    " и даже ",
                    RichTextSpoiler(text="спойлер"),
                    ".",
                ]),
            ],
            credit="Отдел аналитики",
        ),
        InputRichBlockDivider(),
        InputRichBlockFooter(text=[
            "1. Цифры выдуманы для примера и ничего не отражают. ",
            RichTextAnchor(name="note-1"),
            RichTextAnchorLink(text="↩️", anchor_name="ref-1"),
        ]),
    ])


@router.message(Command("sendrichblocks"))
async def cmd_send_rich_blocks(
        message: Message,
) -> None:
    # Заполнено поле blocks, поэтому markdown и html передавать нельзя:
    # ровно одно из трёх полей.
    await message.answer_rich(
        rich_message=build_report(),
    )
