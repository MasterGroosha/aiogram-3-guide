import re
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters.builtin import CommandStart
from .. import dbworker

# Компилируем регулярку при первом импорте модуля
# Сама регулярка взята отсюда: https://stackoverflow.com/questions/3717115/regular-expression-for-youtube-links
yt_regex_pattern = r"(?:https?:\/\/)?(?:www\.)?youtu(?:\.be\/|be.com\/\S*(?:watch|embed)(?:(?:(?=\/[^&\s\?]+(?!\S))\/)|(?:\S*v=|v\/)))([^&\s\?]+)"
yt_regex = re.compile(yt_regex_pattern, re.IGNORECASE)


class Links(StatesGroup):
    add_link_url = State()
    add_link_description = State()


async def cmd_add_link(message: types.Message):
    await message.answer(
        "Отправьте отдельно ссылку на YouTube-видео для добавления в инлайн-режим бота.\n\n"
        "Поддерживаемые форматы ссылок:\n"
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ\n"
        "https://youtu.be/dQw4w9WgXcQ",
        disable_web_page_preview=True
    )
    await Links.add_link_url.set()


async def link_added(message: types.Message, state: FSMContext):
    match_result = re.match(yt_regex, message.text)
    if not match_result:
        await message.reply("Не удалось определить ссылку в этом сообщении. Пожалуйста, попробуйте ещё раз "
                            "или нажмите /cancel, чтобы отменить текущее действие.")
        return
    await state.update_data(yt_hash=match_result.group(1))
    await message.answer("Теперь отправьте название видео, под которым оно будет отображаться в поиске")
    await Links.add_link_description.set()


async def description_added(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    dbworker.insert_or_update(message.from_user.id, user_data["yt_hash"], message.text)
    switch_keyboard = types.InlineKeyboardMarkup()
    switch_keyboard.add(types.InlineKeyboardButton(text="Попробовать", switch_inline_query=""))
    switch_keyboard.add(types.InlineKeyboardButton(text="Попробовать здесь", switch_inline_query_current_chat=""))
    await message.answer(
        "Ссылка и описание успешно добавлены в инлайн-режим и "
        "станут доступны в течение пары минут!\n"
        "Полный список сохранённых ссылок: /links",
        reply_markup=switch_keyboard)
    await state.finish()


def register_add_links_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_add_link, commands="add", state="*")
    dp.register_message_handler(cmd_add_link, CommandStart(deep_link="add"), state="*")
    dp.register_message_handler(link_added, state=Links.add_link_url)
    dp.register_message_handler(description_added, state=Links.add_link_description)
