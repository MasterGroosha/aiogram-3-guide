# Импорт необходимых модулей
import asyncio                 # Для работы с асинхронным программированием
import logging                 # Для ведения логов работы бота
from datetime import datetime  # Для работы с датой и временем

# Импорт основных компонентов aiogram
from aiogram import Bot, Dispatcher, types      # Основные классы для создания бота
from aiogram.enums.dice_emoji import DiceEmoji  # Эмодзи для игральных костей
from aiogram.filters.command import Command     # Фильтр для обработки команд

# Импорт конфигурации
from config_reader import config  # Загрузка настроек из файла конфигурации

# Настройка логирования для отображения информации о работе бота
logging.basicConfig(level=logging.INFO)

# Создание экземпляра бота с токеном из конфигурации
bot = Bot(token=config.bot_token.get_secret_value())

# Создание диспетчера для обработки событий
dp = Dispatcher()

# Сохранение времени запуска бота в контексте диспетчера
# Это значение будет доступно во всех хэндлерах через dependency injection
dp["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")


# Хэндлер на команду /start
# Декоратор автоматически регистрирует функцию как обработчик
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start - приветствует пользователя"""
    await message.answer("Привет!")


# Хэндлер на команду /test1
# Простой пример обработки команды с использованием декоратора
@dp.message(Command("test1"))
async def cmd_test1(message: types.Message):
    """Обработчик команды /test1 - отправляет тестовое сообщение"""
    await message.reply("Тест 1")


# Хэндлер на команду /test2
# Без декоратора, т.к. регистрируется вручную в функции main()
# Это альтернативный способ регистрации хэндлеров
async def cmd_test2(message: types.Message):
    """Обработчик команды /test2 - демонстрирует ручную регистрацию"""
    await message.reply("Тест 2")


@dp.message(Command("answer"))
async def cmd_answer(message: types.Message):
    """Демонстрация метода answer() - отправляет обычный ответ"""
    await message.answer("Это простой ответ")


@dp.message(Command("reply"))
async def cmd_reply(message: types.Message):
    """Демонстрация метода reply() - отправляет ответ с цитированием"""
    await message.reply('Это ответ с "ответом"')


@dp.message(Command("dice"))
async def cmd_dice(message: types.Message):
    """Отправка игрового кубика - демонстрация специальных типов сообщений"""
    await message.answer_dice(emoji=DiceEmoji.DICE)


@dp.message(Command("add_to_list"))
async def cmd_add_to_list(message: types.Message, mylist: list[int]):
    """
    Демонстрация dependency injection - получаем список из контекста диспетчера
    mylist передается автоматически при запуске бота
    """
    mylist.append(7)
    await message.answer("Добавлено число 7")


@dp.message(Command("show_list"))
async def cmd_show_list(message: types.Message, mylist: list[int]):
    """Показывает текущее содержимое списка из контекста"""
    await message.answer(f"Ваш список: {mylist}")


@dp.message(Command("info"))
async def cmd_info(message: types.Message, started_at: str):
    """
    Демонстрация получения данных из контекста диспетчера
    started_at автоматически передается из dp["started_at"]
    """
    await message.answer(f"Бот запущен {started_at}")


async def main():
    """Главная функция для настройки и запуска бота"""
    
    # Демонстрация ручной регистрации хэндлера
    # Альтернатива использованию декораторов
    dp.message.register(cmd_test2, Command("test2"))

    # Запуск бота и пропуск всех накопленных обновлений.
    # Полезно при перезапуске бота для избежания обработки старых сообщений.
    # И да, данный метод можно использовать даже если у вас поллинг.
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запуск бота в режиме long polling
    # mylist=[1, 2, 3] передается в контекст диспетчера для dependency injection
    await dp.start_polling(bot, mylist=[1, 2, 3])


if __name__ == "__main__":
    # Запуск основной функции в асинхронном режиме
    # Точка входа в программу
    asyncio.run(main())
