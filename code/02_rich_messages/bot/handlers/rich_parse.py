from aiogram import F, Router
from aiogram.types import Message

router = Router(name="rich_parse")


def flatten_text(node) -> str:
    """
    Собирает «голый» текст из дерева RichText.
    Узлом может быть строка, список узлов или стилизованный узел,
    у которого внутри лежит ещё один RichText (в поле text).
    Рекурсивно спускаемся до строк и склеиваем их.
    """
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "".join(flatten_text(item) for item in node)
    # У кастомных эмодзи нет вложенного text, зато есть альтернативный текст
    if getattr(node, "type", None) == "custom_emoji":
        return node.alternative_text
    return flatten_text(getattr(node, "text", None))


@router.message(F.rich_message)
async def on_rich_message(
        message: Message,
) -> None:
    # Сюда попадают входящие rich messages — например, пересланные
    blocks = message.rich_message.blocks

    # 1. Перечисляем блоки в порядке их появления
    stats = "\n".join(f"• {block.type}" for block in blocks)

    # 2. Собираем оглавление по заголовкам (блоки типа heading)
    headings = [
        flatten_text(block.text)
        for block in blocks
        if block.type == "heading"
    ]

    # 3. Если внутри есть таблица — вытащим её первую строку как пример
    table = next((b for b in blocks if b.type == "table"), None)

    lines = [
        f"Rich Message из {len(blocks)} блоков.",
        f"Состав:\n{stats}",
    ]
    if headings:
        toc = "\n".join(f"• {title}" for title in headings)
        lines.append(f"\nЗаголовки:\n{toc}")
    if table is not None:
        first_row = " | ".join(flatten_text(cell.text) for cell in table.cells[0])
        lines.append(f"\nПервая строка таблицы: {first_row}")

    await message.answer("\n".join(lines))
