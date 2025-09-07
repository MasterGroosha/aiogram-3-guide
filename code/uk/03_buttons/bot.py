# Імпорт необхідних модулів для роботи з кнопками та клавіатурами
import asyncio                       # Для асинхронного програмування
import logging                       # Для логування операцій бота
from contextlib import suppress      # Для придушення виключень
from random import randint           # Для генерації випадкових чисел
from typing import Optional          # Для типізації

# Імпорт основних компонентів aiogram
from aiogram import Bot, Dispatcher, types, F                    # Основні класи та утиліти
from aiogram.exceptions import TelegramBadRequest                # Виключення Telegram API
from aiogram.filters import Command                              # Фільтри команд
from aiogram.filters.callback_data import CallbackData          # Фабрика callback даних
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder  # Будівельники клавіатур

# Імпорт конфігурації
from config_reader import config  # Токен бота та налаштування

# Створення екземпляра бота та диспетчера
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()

# Налаштування логування
logging.basicConfig(level=logging.INFO)

# Словник для зберігання даних користувачів (у реальному боті використовуйте базу даних)
user_data = {}


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """
    Обробник команди /start - демонструє звичайну клавіатуру
    Показує базовий приклад ReplyKeyboardMarkup
    """
    # Створення кнопок для звичайної клавіатури
    kb = [
        [
            types.KeyboardButton(text="З пюрешкою"),
            types.KeyboardButton(text="Без пюрешки")
        ],
    ]
    # Створення клавіатури з налаштуваннями
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,  # Автоматичне підлаштування розміру кнопок
        input_field_placeholder="Виберіть спосіб подачі"  # Підказка в полі вводу
    )
    await message.answer("Як подавати котлети?", reply_markup=keyboard)


@dp.message(F.text.lower() == "з пюрешкою")
async def with_puree(message: types.Message):
    """
    Обробник вибору "З пюрешкою" - приховує клавіатуру після вибору
    """
    await message.reply("Відмінний вибір!", reply_markup=types.ReplyKeyboardRemove())


@dp.message(F.text.lower() == "без пюрешки")
async def without_puree(message: types.Message):
    """
    Обробник вибору "Без пюрешки" - залишає клавіатуру видимою
    """
    await message.reply("Так несмачно!")


@dp.message(Command("reply_builder"))
async def reply_builder(message: types.Message):
    """
    Обробник команди /reply_builder - демонструє ReplyKeyboardBuilder
    Показує як створювати динамічні клавіатури з автоматичним розташуванням
    """
    # Використання будівельника для створення клавіатури
    builder = ReplyKeyboardBuilder()
    
    # Додавання кнопок з числами від 1 до 16
    for i in range(1, 17):
        builder.add(types.KeyboardButton(text=str(i)))
    
    # Налаштування розташування: 4 кнопки в ряду
    builder.adjust(4)
    
    await message.answer(
        "Виберіть число:",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


@dp.message(Command("special_buttons"))
async def cmd_special_buttons(message: types.Message):
    """
    Обробник команди /special_buttons - демонструє спеціальні кнопки
    Показує кнопки для запиту геолокації, контакту, опитування тощо
    """
    builder = ReplyKeyboardBuilder()
    
    # Метод row дозволяє явно сформувати ряд з однієї або кількох кнопок
    # Перший ряд складається з двох кнопок...
    builder.row(
        types.KeyboardButton(text="Запросити геолокацію", request_location=True),
        types.KeyboardButton(text="Запросити контакт", request_contact=True)
    )
    
    # ... другий з однієї ...
    builder.row(types.KeyboardButton(
        text="Створити вікторину",
        request_poll=types.KeyboardButtonPollType(type="quiz"))
    )
    
    # ... а третій знову з двох
    builder.row(
        types.KeyboardButton(
            text="Вибрати преміум користувача",
            request_user=types.KeyboardButtonRequestUser(
                request_id=1,
                user_is_premium=True
            )
        ),
        types.KeyboardButton(
            text="Вибрати супергрупу з форумами",
            request_chat=types.KeyboardButtonRequestChat(
                request_id=2,
                chat_is_channel=False,
                chat_is_forum=True
            )
        )
    )
    # WebApp-ів поки немає, вибачте :(

    await message.answer(
        "Виберіть дію:",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


@dp.message(F.user_shared)
async def on_user_shared(message: types.Message):
    """
    Обробник поділеного користувача - спрацьовує при натисканні кнопки запиту користувача
    """
    print(
        f"Запит {message.user_shared.request_id}. "
        f"ID користувача: {message.user_shared.user_id}"
    )


@dp.message(F.chat_shared)
async def on_chat_shared(message: types.Message):
    """
    Обробник поділеного чату - спрацьовує при натисканні кнопки запиту чату
    """
    print(
        f"Запит {message.chat_shared.request_id}. "
        f"ID чату: {message.chat_shared.chat_id}"
    )


@dp.message(Command("inline_url"))
async def cmd_inline_url(message: types.Message, bot: Bot):
    """
    Обробник команди /inline_url - демонструє інлайн-кнопки з URL
    Показує різні типи посилань: веб-сайти, Telegram-посилання, користувачі
    """
    builder = InlineKeyboardBuilder()
    
    # Кнопка з посиланням на веб-сайт
    builder.row(types.InlineKeyboardButton(
        text="GitHub", url="https://github.com")
    )
    
    # Кнопка з Telegram-посиланням
    builder.row(types.InlineKeyboardButton(
        text="Оф. канал Telegram",
        url="tg://resolve?domain=telegram")
    )

    # Щоб мати можливість показати ID-кнопку,
    # у користувача повинен бути False прапор has_private_forwards
    user_id = 1234567890
    chat_info = await bot.get_chat(user_id)
    if not chat_info.has_private_forwards:
        builder.row(types.InlineKeyboardButton(
            text="Якийсь користувач",
            url=f"tg://user?id={user_id}")
        )
    
    await message.answer(
        'Виберіть посилання',
        reply_markup=builder.as_markup(),
    )


@dp.message(Command("random"))
async def cmd_random(message: types.Message):
    """
    Обробник команди /random - демонструє callback-кнопки
    Показує основи роботи з інлайн-кнопками та callback_data
    """
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Натисни мене",
        callback_data="random_value")
    )
    await message.answer(
        "Натисніть на кнопку, щоб бот надіслав число від 1 до 10",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data == "random_value")
async def send_random_value(callback: types.CallbackQuery):
    """
    Обробник callback-запиту - відповідає на натискання кнопки
    Показує як обробляти callback-запити та відправляти відповіді
    """
    await callback.message.answer(str(randint(1, 10)))
    await callback.answer(
        text="Дякуємо, що скористалися ботом!",
        show_alert=True  # Показати повідомлення у вигляді алерту
    )
    # або просто await callback.answer()


# ----------
# Це варіант БЕЗ фабрики callback даних

def get_keyboard():
    """
    Функція для створення інлайн-клавіатури без фабрики
    Демонструє статичне створення кнопок
    """
    buttons = [
        [
            types.InlineKeyboardButton(text="-1", callback_data="num_decr"),
            types.InlineKeyboardButton(text="+1", callback_data="num_incr")
        ],
        [types.InlineKeyboardButton(text="Підтвердити", callback_data="num_finish")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def update_num_text(message: types.Message, new_value: int):
    """
    Функція для оновлення тексту повідомлення з новим значенням
    Використовує suppress для ігнорування помилок редагування
    """
    with suppress(TelegramBadRequest):
        await message.edit_text(
            f"Вкажіть число: {new_value}",
            reply_markup=get_keyboard()
        )


@dp.message(Command("numbers"))
async def cmd_numbers(message: types.Message):
    """
    Обробник команди /numbers - демонструє інтерактивну зміну значень
    Показує роботу з callback-даними без фабрики
    """
    user_data[message.from_user.id] = 0
    await message.answer("Вкажіть число: 0", reply_markup=get_keyboard())


@dp.callback_query(F.data.startswith("num_"))
async def callbacks_num(callback: types.CallbackQuery):
    """
    Обробник callback-запитів для зміни числа - варіант без фабрики
    Обробляє натискання кнопок +1, -1 та підтвердження
    """
    user_value = user_data.get(callback.from_user.id, 0)
    action = callback.data.split("_")[1]

    if action == "incr":
        user_data[callback.from_user.id] = user_value + 1
        await update_num_text(callback.message, user_value + 1)
    elif action == "decr":
        user_data[callback.from_user.id] = user_value - 1
        await update_num_text(callback.message, user_value - 1)
    elif action == "finish":
        await callback.message.edit_text(f"Підсумок: {user_value}")

    await callback.answer()


# ----------
# Це варіант з фабрикою callback даних

class NumbersCallbackFactory(CallbackData, prefix="fabnum"):
    """
    Фабрика callback даних для роботи з числами
    Демонструє структурований підхід до callback-даних
    """
    action: str                    # Дія (change, finish)
    value: Optional[int] = None    # Значення для зміни (опціонально)


def get_keyboard_fab():
    """
    Функція для створення інлайн-клавіатури з фабрикою
    Демонструє використання CallbackData для структурованих даних
    """
    builder = InlineKeyboardBuilder()
    
    # Додавання кнопок зі структурованими callback-даними
    builder.button(text="-2", callback_data=NumbersCallbackFactory(action="change", value=-2))
    builder.button(text="-1", callback_data=NumbersCallbackFactory(action="change", value=-1))
    builder.button(text="+1", callback_data=NumbersCallbackFactory(action="change", value=1))
    builder.button(text="+2", callback_data=NumbersCallbackFactory(action="change", value=2))
    builder.button(text="Підтвердити", callback_data=NumbersCallbackFactory(action="finish"))
    
    # Розташування: 4 кнопки в ряду
    builder.adjust(4)
    return builder.as_markup()


async def update_num_text_fab(message: types.Message, new_value: int):
    """
    Функція для оновлення тексту повідомлення з фабрикою
    Аналогічна попередній функції, але для варіанту з фабрикою
    """
    with suppress(TelegramBadRequest):
        await message.edit_text(
            f"Вкажіть число: {new_value}",
            reply_markup=get_keyboard_fab()
        )


@dp.message(Command("numbers_fab"))
async def cmd_numbers_fab(message: types.Message):
    """
    Обробник команди /numbers_fab - демонструє використання фабрики callback даних
    Показує більш структурований підхід до callback-даних
    """
    user_data[message.from_user.id] = 0
    await message.answer("Вкажіть число: 0", reply_markup=get_keyboard_fab())


# Натискання на одну з кнопок: -2, -1, +1, +2
@dp.callback_query(NumbersCallbackFactory.filter(F.action == "change"))
async def callbacks_num_change_fab(callback: types.CallbackQuery, callback_data: NumbersCallbackFactory):
    """
    Обробник зміни значення з фабрикою - варіант з фабрикою callback даних
    Демонструє автоматичне розпарсювання callback-даних через фільтр
    """
    # Поточне значення
    user_value = user_data.get(callback.from_user.id, 0)

    # Зміна значення на вказану величину
    user_data[callback.from_user.id] = user_value + callback_data.value
    await update_num_text_fab(callback.message, user_value + callback_data.value)
    await callback.answer()


# Натискання на кнопку "підтвердити"
@dp.callback_query(NumbersCallbackFactory.filter(F.action == "finish"))
async def callbacks_num_finish_fab(callback: types.CallbackQuery):
    """
    Обробник підтвердження з фабрикою - завершує роботу з числом
    """
    # Поточне значення
    user_value = user_data.get(callback.from_user.id, 0)

    await callback.message.edit_text(f"Підсумок: {user_value}")
    await callback.answer()


# Запуск бота
async def main():
    """
    Основна функція для запуску бота
    Налаштовує polling та обробляє очищення
    """
    # Запускаємо бота та пропускаємо всі накопичені вхідні повідомлення
    # Так, цей метод можна викликати навіть якщо у вас polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Запуск основної функції в асинхронному режимі
    asyncio.run(main())