def trim_text_smart(
        text: str,
        max_len: int = 4000,
        trim_marker: str = "…",
) -> str:
    """
    Обрезает текст до {max_len} символов,
    стараясь это делать по пробелу или \n
    :param text: исходный текст
    :param max_len: максимально разрешённая длина текста
    :param trim_marker: символ, которым обрезается текст
    :return: обрезанный текст
    """
    if len(text) <= max_len:
        return text

    cut_len = max_len - len(trim_marker)
    candidate = text[:cut_len]

    # Пытаемся резать по границе строки
    newline_pos = candidate.rfind("\n")
    if newline_pos != -1:
        return candidate[:newline_pos] + trim_marker

    # Если нет — по последнему пробелу
    space_pos = candidate.rfind(" ")
    if space_pos != -1:
        return candidate[:space_pos] + trim_marker

    # Совсем крайний случай
    return candidate + trim_marker


def smart_capitalize(s: str) -> str:
    """
    Принимает на вход строку и делает только первый символ большим (uppercase),
    остальные никак не трогает.
    Если строка пустая, возвращает пустую строку.
    Если строка начинается с цифры, то ничего не делает, возвращает строку как есть.
    Если строка начинается с кавычки (варианты: ", ', «),
    то делает большой (uppercase) только следующий буквенный символ,
    если перед этим не было цифры.
    Если строка из одного символа, то если это буква (неважно, английская или русская),
    то делает её большой.
    :param s: исходная строка
    :return: отформатированная строка
    """
    if not s:
        return ""

    # Один символ
    if len(s) == 1:
        return s.upper() if s.isalpha() else s

    # Если начинается с цифры — ничего не делаем
    if s[0].isdigit():
        return s

    quotes = {'"', "'", "«"}
    # Если начинается с кавычки
    if s[0] in quotes:
        for i in range(1, len(s)):
            char = s[i]

            # Если перед буквой была цифра — выходим, ничего не меняем
            if char.isdigit():
                return s

            if char.isalpha():
                return s[:i] + char.upper() + s[i+1:]

        return s  # если букв так и не нашли

    # Обычный случай: первый символ — буква
    if s[0].isalpha():
        return s[0].upper() + s[1:]

    return s