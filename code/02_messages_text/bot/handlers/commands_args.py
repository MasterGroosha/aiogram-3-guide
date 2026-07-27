from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

router = Router(name="commands_args")


@router.message(Command("settimer"))
async def cmd_settimer(
        message: Message,
        command: CommandObject
) -> None:
    # Если не переданы никакие аргументы, то
    # command.args будет None
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return
    # Пробуем разделить аргументы на две части по первому встречному пробелу
    try:
        delay_time, text_to_send = command.args.split(" ", maxsplit=1)
    # Если получилось меньше двух частей, вылетит ValueError
    except ValueError:
        await message.answer(
            "Ошибка: неправильный формат команды. Пример:\n"
            "/settimer <time> <message>"
        )
        return
    await message.answer(
        "Таймер добавлен!\n"
        f"Время: {delay_time}\n"
        f"Текст: {text_to_send}"
    )


@router.message(Command("custom1", prefix="%"))
async def cmd_custom1(message: Message) -> None:
    await message.answer("Вижу команду!")


# Можно указать несколько префиксов........vv...
@router.message(Command("custom2", prefix="/!"))
async def cmd_custom2(message: Message) -> None:
    await message.answer("И эту тоже вижу!")
