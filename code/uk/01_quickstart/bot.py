# Імпорт необхідних модулів
import asyncio                 # Для роботи з асинхронним програмуванням
import logging                 # Для ведення логів роботи бота
from datetime import datetime  # Для роботи з датою та часом

# Імпорт основних компонентів aiogram
from aiogram import Bot, Dispatcher, types      # Основні класи для створення бота
from aiogram.enums.dice_emoji import DiceEmoji  # Емодзі для ігрових кубиків
from aiogram.filters.command import Command     # Фільтр для обробки команд

# Імпорт конфігурації
from config_reader import config  # Завантаження налаштувань з файлу конфігурації

# Налаштування логування для відображення інформації про роботу бота
logging.basicConfig(level=logging.INFO)

# Створення екземпляра бота з токеном з конфігурації
bot = Bot(token=config.bot_token.get_secret_value())

# Створення диспетчера для обробки подій
dp = Dispatcher()

# Збереження часу запуску бота в контексті диспетчера
# Це значення буде доступне у всіх хендлерах через dependency injection
dp["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")


# Хендлер для команди /start
# Декоратор автоматично реєструє функцію як обробник
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обробник команди /start - вітає користувача"""
    await message.answer("Привіт!")


# Хендлер для команди /test1
# Простий приклад обробки команди з використанням декоратора
@dp.message(Command("test1"))
async def cmd_test1(message: types.Message):
    """Обробник команди /test1 - надсилає тестове повідомлення"""
    await message.reply("Тест 1")


# Хендлер для команди /test2
# Без декоратора, оскільки реєструється вручну в функції main()
# Це альтернативний спосіб реєстрації хендлерів
async def cmd_test2(message: types.Message):
    """Обробник команди /test2 - демонструє ручну реєстрацію"""
    await message.reply("Тест 2")


@dp.message(Command("answer"))
async def cmd_answer(message: types.Message):
    """Демонстрація методу answer() - надсилає звичайну відповідь"""
    await message.answer("Це проста відповідь")


@dp.message(Command("reply"))
async def cmd_reply(message: types.Message):
    """Демонстрація методу reply() - надсилає відповідь з цитуванням"""
    await message.reply('Це відповідь з "відповіддю"')


@dp.message(Command("dice"))
async def cmd_dice(message: types.Message):
    """Надсилання ігрового кубика - демонстрація спеціальних типів повідомлень"""
    await message.answer_dice(emoji=DiceEmoji.DICE)


@dp.message(Command("add_to_list"))
async def cmd_add_to_list(message: types.Message, mylist: list[int]):
    """
    Демонстрація dependency injection - отримуємо список з контексту диспетчера
    mylist передається автоматично при запуску бота
    """
    mylist.append(7)
    await message.answer("Додано число 7")


@dp.message(Command("show_list"))
async def cmd_show_list(message: types.Message, mylist: list[int]):
    """Показує поточний вміст списку з контексту"""
    await message.answer(f"Ваш список: {mylist}")


@dp.message(Command("info"))
async def cmd_info(message: types.Message, started_at: str):
    """
    Демонстрація отримання даних з контексту диспетчера
    started_at автоматично передається з dp["started_at"]
    """
    await message.answer(f"Бот запущено {started_at}")


async def main():
    """Головна функція для налаштування та запуску бота"""
    
    # Демонстрація ручної реєстрації хендлера
    # Альтернатива використанню декораторів
    dp.message.register(cmd_test2, Command("test2"))

    # Запуск бота та пропуск всіх накопичених оновлень.
    # Корисно при перезапуску бота для уникнення обробки старих повідомлень.
    # І так, цей метод можна використовувати навіть якщо у вас polling.
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запуск бота в режимі long polling
    # mylist=[1, 2, 3] передається в контекст диспетчера для dependency injection
    await dp.start_polling(bot, mylist=[1, 2, 3])


if __name__ == "__main__":
    # Запуск основної функції в асинхронному режимі
    # Точка входу в програму
    asyncio.run(main())
