from typing import Optional

# В реальной жизни здесь должна быть нормальная СУБД.
# Но для примера нам будет достаточно показать на обычном словаре.
# Учтите, что он сбрасывается при перезапуске бота.
data = dict()


def add_link(
        telegram_id: int,
        link: str,
        title: str,
        description: Optional[str]
):
    """
    Сохраняет ссылку в словарь

    :param telegram_id: ID юзера в Telegram
    :param link: текст ссылки
    :param title: заголовок ссылки
    :param description: (опционально) описание ссылки
    """
    data.setdefault(telegram_id, dict())
    data[telegram_id].setdefault("links", dict())
    data[telegram_id]["links"][link] = {
        "title": title,
        "description": description
    }


def add_photo(
        telegram_id: int,
        photo_file_id: str,
        photo_unique_id: str
):
    """
    Сохраняет изображение в словарь

    :param telegram_id: ID юзера в Telegram
    :param photo_file_id: file_id изображения
    :param photo_unique_id: file_unique_id изображения
    """
    data.setdefault(telegram_id, dict())
    data[telegram_id].setdefault("images", [])
    if photo_file_id not in data[telegram_id]["images"]:
        data[telegram_id]["images"].append((photo_file_id, photo_unique_id))


def get_links_by_id(telegram_id: int) -> dict:
    """
    Получает сохранённые ссылки пользователя

    :param telegram_id: ID юзера в Telegram
    :return: если по юзеру есть данные, то словарь со ссылками
    """
    if telegram_id in data and "links" in data[telegram_id]:
        return data[telegram_id]["links"]
    return dict()


def get_images_by_id(telegram_id: int) -> list[str]:
    """
    Получает сохранённые изображения пользователя

    :param telegram_id: ID юзера в Telegram
    :return:
    """
    if telegram_id in data and "images" in data[telegram_id]:
        return [item[0] for item in data[telegram_id]["images"]]
    return []


def delete_link(telegram_id: int, link: str):
    """
    Удаляет ссылку

    :param telegram_id: ID юзера в Telegram
    :param link: ссылка
    """
    if telegram_id in data:
        if "links" in data[telegram_id]:
            if link in data[telegram_id]["links"]:
                del data[telegram_id]["links"][link]


def delete_image(telegram_id: int, photo_file_unique_id: str):
    """
    Удаляет изображение

    :param telegram_id: ID юзера в Telegram
    :param photo_file_unique_id: file_unique_id изображения для удаления
    """
    if telegram_id in data and "images" in data[telegram_id]:
        for index, (_, unique_id) in enumerate(data[telegram_id]["images"]):
            if unique_id == photo_file_unique_id:
                data[telegram_id]["images"].pop(index)
