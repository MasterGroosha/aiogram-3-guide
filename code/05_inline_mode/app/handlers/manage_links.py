import re
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Text, CommandStart
from aiogram.utils.deep_linking import get_start_link
from aiogram.utils.markdown import quote_html
from .. import dbworker


async def get_view_links_entry(yt_hash: str, description: str):
    start_link = await get_start_link("del_"+yt_hash)
    print(start_link)
    return (f"• <b>{quote_html(description)}</b>\n"
            f"https://youtu.be/{yt_hash}\n<a href=\"{start_link}\">Удалить</a>")


async def view_links(message: types.Message, state: FSMContext):
    await state.finish()
    links = dbworker.get_links(message.from_user.id)
    if len(links) == 0:
        return await message.answer("У вас нет сохранённых ссылок!")

    # Note: в реальном боте здесь надо сделать пагинацию (постраничный просмотр), т.к. количество
    # сохранённых ссылок может быть большим
    items = [await get_view_links_entry(item[0], item[1]) for item in links]
    await message.answer("\n".join(items), disable_web_page_preview=True, parse_mode="HTML")


async def delete_link(message: types.Message, state: FSMContext):
    await state.finish()
    args = message.text.split("_", maxsplit=1)
    if len(args) == 1:
        return await message.answer("Неправильный формат команды!")
    dbworker.delete(message.from_user.id, args[1])
    await message.answer("Ссылка успешно удалена! Список сохранённых ссылок: /links")


def register_manage_links_handlers(dp: Dispatcher):
    dp.register_message_handler(view_links, commands="links", state="*")
    dp.register_message_handler(delete_link, CommandStart(deep_link=re.compile(r'^del_.*$')), state="*")
