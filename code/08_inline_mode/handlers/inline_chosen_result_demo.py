from aiogram import Router
from aiogram.types import ChosenInlineResult

router = Router()


@router.chosen_inline_result()
async def pagination_demo(
        chosen_result: ChosenInlineResult,
):
    print(
        f"After '{chosen_result.query}' query, "
        f"user chose option with ID '{chosen_result.result_id}'"
    )
