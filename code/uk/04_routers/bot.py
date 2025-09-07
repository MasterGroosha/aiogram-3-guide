# Імпорт необхідних модулів для роботи з маршрутизацією
import asyncio                           # Для асинхронного програмування

# Імпорт основних компонентів aiogram
from aiogram import Bot, Dispatcher     # Основні класи aiogram

# Імпорт конфігурації та обробників
from config_reader import config        # Налаштування бота
from handlers import questions, different_types  # Модулі з обробниками


# Запуск бота
async def main():
    """
    Основна функція для запуску бота
    Демонструє організацію коду з використанням роутерів
    """
    # Створення екземплярів бота та диспетчера
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()

    # Підключення роутерів - порядок важливий!
    # Роутери обробляють повідомлення в порядку підключення
    dp.include_routers(questions.router, different_types.router)

    # Альтернативний варіант реєстрації роутерів по одному на рядок
    # dp.include_router(questions.router)
    # dp.include_router(different_types.router)

    # Запускаємо бота та пропускаємо всі накопичені вхідні повідомлення
    # Так, цей метод можна викликати навіть якщо у вас поллінг
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Запуск основної функції в асинхронному режимі
    asyncio.run(main())