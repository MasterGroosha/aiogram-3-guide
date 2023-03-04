from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from filters import HasLinkFilter, ViaBotFilter
from states import DeleteCommon
from storage import delete_link, delete_image

router = Router()


@router.message(
    DeleteCommon.waiting_for_delete_start,
    F.text,
    ViaBotFilter(),
    HasLinkFilter()
)
async def link_deletion_handler(message: Message, link: str, state: FSMContext):
    delete_link(message.from_user.id, link)
    await state.clear()
    await message.answer(
        text="Ссылка удалена! "
             "Выдача инлайн-режима обновится в течение нескольких минут.")


@router.message(
    DeleteCommon.waiting_for_delete_start,
    F.photo[-1].file_unique_id.as_("file_unique_id"),
    ViaBotFilter()
)
async def image_deletion_handler(
        message: Message,
        state: FSMContext,
        file_unique_id: str
):
    delete_image(message.from_user.id, file_unique_id)
    await state.clear()
    await message.answer(
        text="Изображение удалено! "
             "Выдача инлайн-режима обновится в течение нескольких минут.")
