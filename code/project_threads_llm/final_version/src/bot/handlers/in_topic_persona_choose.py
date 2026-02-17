import structlog
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from structlog.typing import FilteringBoundLogger

from bot.callback_factories import ChoosePromptFactory
from bot.prompts import available_personas, prompts
from bot.states import NewChatFlow
from bot.storage import memory_chat_storage

router = Router()
logger: FilteringBoundLogger = structlog.get_logger()


@router.callback_query(
    ChoosePromptFactory.filter(),
    NewChatFlow.choosing_persona,
)
async def prompt_chosen_correct_state(
        callback: CallbackQuery,
        callback_data: ChoosePromptFactory,
        state: FSMContext,
):
    # Проверяем, что такая персона ещё существует
    if callback_data.style not in available_personas():
        await callback.answer(
            text="Что-то пошло не так. Пожалуйста, создайте новый чат.",
            show_alert=True,
        )
        return
    # Получаем виртуальный чат для этого топика и сохраняем выбранные данные
    llm_chat = await memory_chat_storage.get(
        user_id=callback.from_user.id,
        thread_id=callback.message.message_thread_id,
    )
    llm_chat.meta.prompt_key = callback_data.style
    temperature = prompts[callback_data.style]["temperature"]
    llm_chat.meta.temperature = temperature
    await memory_chat_storage.update(
        user_id=callback.from_user.id,
        thread_id=callback.message.message_thread_id,
        new_version=llm_chat,
    )
    await state.set_state(None)
    await callback.message.edit_text(
        f"Выбран пресет: {prompts[callback_data.style]["name"]}\n\n"
        f"Пожалуйста, теперь напишите ваш запрос боту.",
        reply_markup=None,
    )
    await callback.answer()
