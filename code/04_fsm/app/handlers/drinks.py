from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


available_drinks_names = ["чай", "кофе", "какао"]
available_drinks_sizes = ["250мл", "0.5л", "1л"]


class OrderDrinks(StatesGroup):
    waiting_for_drink_name = State()
    waiting_for_drink_size = State()


async def drinks_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in available_drinks_names:
        keyboard.add(name)
    await message.answer("Выберите напиток:", reply_markup=keyboard)
    await OrderDrinks.waiting_for_drink_name.set()


async def drinks_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_drinks_names:
        await message.answer("Пожалуйста, выберите напиток, используя клавиатуру ниже.")
        return
    await state.update_data(chosen_food=message.text.lower())

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for size in available_drinks_sizes:
        keyboard.add(size)
    # для простых шагов можно не указывать название состояния, обходясь next()
    await OrderDrinks.next()
    await message.answer("Теперь выберите размер порции:", reply_markup=keyboard)


async def drinks_size_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_drinks_sizes:
        await message.answer("Пожалуйста, выберите размер порции, используя клавиатуру ниже.")
        return
    user_data = await state.get_data()
    await message.answer(f"Вы заказали {user_data['chosen_food']} объёмом {message.text.lower()}.\n"
                         f"Попробуйте теперь заказать еду: /food", reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


def register_handlers_drinks(dp: Dispatcher):
    dp.register_message_handler(drinks_start, commands="drinks", state="*")
    dp.register_message_handler(drinks_chosen, state=OrderDrinks.waiting_for_drink_name)
    dp.register_message_handler(drinks_size_chosen, state=OrderDrinks.waiting_for_drink_size)
