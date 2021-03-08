import logging
from aiogram import Dispatcher, types
from aiogram.utils.markdown import quote_html
from .. import dbworker


async def inline_handler(query: types.InlineQuery):
    user_links = dbworker.get_links(query.from_user.id, query.query or None)
    if len(user_links) == 0:
        switch_text = "У вас нет сохранённых ссылок. Добавить »»" \
            if len(query.query) == 0 \
            else "Не найдено ссылок по данному запросу. Добавить »»"
        return await query.answer(
            [], cache_time=60, is_personal=True,
            switch_pm_parameter="add", switch_pm_text=switch_text)
    articles = [types.InlineQueryResultArticle(
        id=item[0],
        title=item[1],
        description=f"https://youtu.be/{item[0]}",
        url=f"https://youtu.be/{item[0]}",
        hide_url=False,
        thumb_url=f"https://img.youtube.com/vi/{item[0]}/1.jpg",
        input_message_content=types.InputTextMessageContent(
            message_text=f"<b>{quote_html(item[1])}</b>\nhttps://youtu.be/{item[0]}",
            parse_mode="HTML"
        )
    ) for item in user_links]
    await query.answer(articles, cache_time=60, is_personal=True,
                       switch_pm_text="Добавить ссылку »»", switch_pm_parameter="add")


# Генератор фейковых инлайн-объектов для фукнции inline_handler_extra (ниже)
def get_fake_results(start_num: int, size: int = 50):
    overall_items = 195
    # Если результатов больше нет, отправляем пустой список
    if start_num >= overall_items:
        return []
    # Отправка неполной пачки (последней)
    elif start_num + size >= overall_items:
        return list(range(start_num, overall_items+1))
    else:
        return list(range(start_num, start_num+size))


# Инлайн-хэндлер из секции дополнительных материалов
# Не зарегистрирован и не используется
async def inline_handler_extra(query: types.InlineQuery):
    # Высчитываем offset как число
    query_offset = int(query.offset) if query.offset else 1
    results = [types.InlineQueryResultArticle(
        id=str(item_num),
        title=f"Объект №{item_num}",
        input_message_content=types.InputTextMessageContent(
            message_text=f"Объект №{item_num}"
        )
    ) for item_num in get_fake_results(query_offset)]
    if len(results) < 50:
        # Результатов больше не будет, next_offset пустой
        await query.answer(results, is_personal=True, next_offset="")
    else:
        # Ожидаем следующую пачку
        await query.answer(results, is_personal=True, next_offset=str(query_offset+50))


# Хэндлер для сбора статистики (не забудьте включить сбор у @BotFather)
async def chosen_handler(chosen_result: types.ChosenInlineResult):
    logging.info(f"Chosen query: {chosen_result.query}"
                 f"from user: {chosen_result.from_user.id}")


def register_inline_handlers(dp: Dispatcher):
    dp.register_inline_handler(inline_handler, state="*")
    dp.register_chosen_inline_handler(chosen_handler, state="*")
