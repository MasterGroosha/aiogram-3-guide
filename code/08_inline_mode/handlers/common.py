from aiogram import Router, F
from aiogram.filters.command import Command, CommandStart
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, \
    InlineKeyboardMarkup, InlineKeyboardButton

from states import SaveCommon, DeleteCommon

router = Router()


@router.message(CommandStart(magic=F.args == "add"))
@router.message(Command("save"), StateFilter(None))
async def cmd_save(message: Message, state: FSMContext):
    await message.answer(
        text="Давай что-нибудь сохраним. "
             "Пришли мне какую-нибудь ссылку или картинку. "
             "Если передумаешь — шли /cancel"
    )
    await state.set_state(SaveCommon.waiting_for_save_start)


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Тут какой-нибудь стартовый текст. Придумайте сами.",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command("delete"), StateFilter(None))
async def cmd_delete(message: Message, state: FSMContext):
    kb = []
    kb.append([
        InlineKeyboardButton(
            text="Выбрать ссылку",
            switch_inline_query_current_chat="links"
        )
    ])
    kb.append([
        InlineKeyboardButton(
            text="Выбрать изображение",
            switch_inline_query_current_chat="images"
        )
    ])
    await state.set_state(DeleteCommon.waiting_for_delete_start)
    await message.answer(
        text="Выберите, что хотите удалить:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )


@router.message(Command(commands=["cancel"]))
async def cmd_save(message: Message, state: FSMContext):
    await message.answer("Действие отменено")
    await state.clear()
