# Імпорт необхідних модулів для роботи з повідомленнями та медіа
import asyncio                 # Для асинхронного програмування
import logging                 # Для логування операцій бота
import re                      # Для регулярних виразів у обробці deep link'ів
from datetime import datetime  # Для роботи з часом у повідомленнях

# Імпорт основних компонентів aiogram
from aiogram import Bot, Dispatcher, html, F                                                         # Основні класи та утиліти aiogram
from aiogram.client.default import DefaultBotProperties                                              # Налаштування бота за замовчуванням
from aiogram.enums import ParseMode                                                                  # Режими форматування тексту (HTML, Markdown)
from aiogram.filters import Command, CommandObject, CommandStart                                     # Фільтри команд
from aiogram.types import Message, FSInputFile, URLInputFile, BufferedInputFile, LinkPreviewOptions  # Типи повідомлень та файлів
from aiogram.utils.formatting import as_list, as_marked_section, Bold, as_key_value, HashTag         # Утиліти форматування тексту
from aiogram.utils.markdown import hide_link                                                         # Утиліта прихованих посилань
from aiogram.utils.media_group import MediaGroupBuilder                                              # Для створення альбомів

# Імпорт конфігурації
from config_reader import config  # Токен бота та налаштування

# Створення екземпляра бота з HTML парсингом за замовчуванням
# Це означає, що всі повідомлення будуть парситися як HTML, якщо не вказано інше
bot = Bot(
    token=config.bot_token.get_secret_value(),
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML  # Встановлення HTML як режиму парсингу за замовчуванням
    )
)

# Створення диспетчера для обробки подій
dp = Dispatcher()

# Налаштування логування для відображення операцій бота в консолі
logging.basicConfig(level=logging.INFO)


@dp.message(Command("test"))
async def any_message(message: Message):
    """
    Обробник команди /test - демонструє різні режими парсингу
    Показує, як один і той же текст відображається з різним форматуванням
    """
    # HTML форматування (жирний текст)
    await message.answer("Привіт, <b>світе</b>!", parse_mode=ParseMode.HTML)
    
    # Markdown V2 форматування (жирний текст з екранованим знаком оклику)
    await message.answer("Привіт, *світе*\!", parse_mode=ParseMode.MARKDOWN_V2)
    
    # HTML форматування з використанням режиму парсингу бота за замовчуванням (HTML)
    await message.answer("Повідомлення з <u>HTML розміткою</u>")
    
    # Без форматування - parse_mode=None вимикає всю розмітку
    await message.answer("Повідомлення без <s>будь-якої розмітки</s>", parse_mode=None)


@dp.message(Command("hello"))
async def cmd_hello(message: Message):
    """
    Обробник команди /hello - демонструє безпечне форматування тексту
    Використовує html.quote() для екранування спеціальних символів у вводі користувача
    """
    await message.answer(
        f"Привіт, {html.bold(html.quote(message.from_user.full_name))}",
        parse_mode=ParseMode.HTML
    )


@dp.message(Command("advanced_example"))
async def cmd_advanced_example(message: Message):
    """
    Обробник команди /advanced_example - демонструє розширене форматування тексту
    Використовує утиліти форматування aiogram для створення структурованих повідомлень
    """
    # Створення структурованого контенту з використанням утиліт форматування
    content = as_list(
        # Секція успіхів з мітками-галочками
        as_marked_section(
            Bold("Успішно:"),
            "Тест 1",
            "Тест 3", 
            "Тест 4",
            marker="✅ ",  # Зелена галочка для успішних тестів
        ),
        # Секція невдач з мітками X
        as_marked_section(
            Bold("Невдало:"),
            "Тест 2",
            marker="❌ ",  # Червоний хрестик для невдалих тестів
        ),
        # Секція підсумку з парами ключ-значення
        as_marked_section(
            Bold("Підсумок:"),
            as_key_value("Всього", 4),
            as_key_value("Успішно", 3),
            as_key_value("Невдало", 1),
            marker="  ",  # Відступ для елементів підсумку
        ),
        HashTag("#test"),  # Додавання хештегу для категоризації
        sep="\n\n",  # Розділення секцій подвійними переносами рядків
    )
    # Відправка відформатованого контенту
    await message.answer(**content.as_kwargs())


@dp.message(Command("settimer"))
async def cmd_settimer(
        message: Message,
        command: CommandObject  # CommandObject містить аргументи команди
):
    """
    Обробник команди /settimer - демонструє парсинг аргументів команди
    Очікуваний формат: /settimer <час> <повідомлення>
    """
    # Перевірка, чи були надані якісь аргументи
    # Якщо аргументи не передані, то command.args буде None
    if command.args is None:
        await message.answer(
            "Помилка: аргументи не передані"
        )
        return
    
    # Спроба розділити аргументи на дві частини першим знайденим пробілом
    try:
        delay_time, text_to_send = command.args.split(" ", maxsplit=1)
    # Якщо частин менше двох, буде викинуто ValueError
    except ValueError:
        await message.answer(
            "Помилка: неправильний формат команди. Приклад:\n"
            "/settimer <час> <повідомлення>"
        )
        return
    
    # Підтвердження створення таймеру (у реальному боті ви б запустили справжній таймер)
    await message.answer(
        "Таймер додано!\n"
        f"Час: {delay_time}\n"
        f"Текст: {text_to_send}"
    )


@dp.message(Command("gif"))
async def send_gif(message: Message):
    """
    Обробник команди /gif - демонструє відправку анімацій/GIF
    Показує позиціонування підпису над медіа
    """
    await message.answer_animation(
        animation="<gif file_id>",     # Замініть на справжній file_id
        caption="Я сьогодні:",
        show_caption_above_media=True  # Показати підпис над GIF
    )


# Приклади користувацьких префіксів команд
@dp.message(Command("custom1", prefix="%"))
async def cmd_custom1(message: Message):
    """
    Обробник команди %custom1 - демонструє користувацький префікс команди
    Використовує % замість стандартного префіксу /
    """
    await message.answer("Я бачу команду!")


@dp.message(Command("custom2", prefix="/!"))
async def cmd_custom2(message: Message):
    """
    Обробник команд /custom2 або !custom2
    Можна вказати кілька префіксів як рядок
    """
    await message.answer("Я бачу і цю команду!")


# Обробники deep link'ів - кілька способів обробки /start з параметрами
@dp.message(Command("help"))
@dp.message(CommandStart(
    deep_link=True, magic=F.args == "help"  # Відповідає /start help
))
async def cmd_start_help(message: Message):
    """
    Обробник команди /help або deep link /start help
    Демонструє кілька декораторів на одному обробнику
    """
    await message.answer("Це довідкове повідомлення")


@dp.message(CommandStart(
    deep_link=True,
    magic=F.args.regexp(re.compile(r'book_(\d+)'))  # Відповідає /start book_123
))
async def cmd_start_book(
        message: Message,
        command: CommandObject
):
    """
    Обробник deep link'ів /start book_<номер>
    Використовує регулярний вираз для витягування номера книги з параметра deep link
    """
    book_number = command.args.split("_")[1]  # Витягування номера після "book_"
    await message.answer(f"Надсилаю книгу №{book_number}")


@dp.message(Command("links"))
async def cmd_links(message: Message):
    """
    Обробник команди /links - демонструє налаштування попереднього перегляду посилань
    Показує різні способи контролю відображення посилань
    """
    # Два посилання, які будуть включені в підсумкове повідомлення
    links_text = (
        "https://nplus1.ru/news/2024/05/23/voyager-1-science-data"
        "\n"
        "https://t.me/telegram"
    )
    
    # Приклад 1: Повністю вимкнути попередній перегляд посилань
    options_1 = LinkPreviewOptions(is_disabled=True)
    await message.answer(
        f"Без попереднього перегляду посилань\n{links_text}",
        link_preview_options=options_1
    )

    # -------------------- #

    # Приклад 2: Маленький попередній перегляд
    # Для використання prefer_small_media, ви також повинні вказати url
    options_2 = LinkPreviewOptions(
        url="https://nplus1.ru/news/2024/05/23/voyager-1-science-data",
        prefer_small_media=True  # Показати компактний попередній перегляд
    )
    await message.answer(
        f"Маленький попередній перегляд\n{links_text}",
        link_preview_options=options_2
    )

    # -------------------- #

    # Приклад 3: Великий попередній перегляд
    # Для використання prefer_large_media, ви також повинні вказати url
    options_3 = LinkPreviewOptions(
        url="https://nplus1.ru/news/2024/05/23/voyager-1-science-data",
        prefer_large_media=True  # Показати розширений попередній перегляд
    )
    await message.answer(
        f"Великий попередній перегляд\n{links_text}",
        link_preview_options=options_3
    )

    # -------------------- #

    # Приклад 4: Комбінування налаштувань - маленький попередній перегляд над текстом
    options_4 = LinkPreviewOptions(
        url="https://nplus1.ru/news/2024/05/23/voyager-1-science-data",
        prefer_small_media=True,
        show_above_text=True  # Позиціонувати попередній перегляд над текстом повідомлення
    )
    await message.answer(
        f"Маленький попередній перегляд над текстом\n{links_text}",
        link_preview_options=options_4
    )

    # -------------------- #

    # Приклад 5: Вибір якого посилання показувати (не обов'язково першого)
    options_5 = LinkPreviewOptions(
        url="https://t.me/telegram"  # Попередній перегляд другого посилання замість першого
    )
    await message.answer(
        f"Попередній перегляд не першого посилання\n{links_text}",
        link_preview_options=options_5
    )


@dp.message(Command("hidden_link"))
async def cmd_hidden_link(message: Message):
    """
    Обробник команди /hidden_link - демонструє вбудовування невидимих посилань
    Використовує hide_link() для невидимого вбудовування зображення в повідомлення
    """
    await message.answer(
        f"{hide_link('https://telegra.ph/file/562a512448876923e28c3.png')}"
        f"Документація Telegram: *існує*\n"
        f"Користувачі: *не читають документацію*\n"
        f"Groosha:"
    )


@dp.message(Command('images'))
async def upload_photo(message: Message):
    """
    Обробник команди /images - демонструє різні способи відправки зображень
    Показує різні типи InputFile для відправки фотографій в Telegram
    """
    # Тут ми будемо зберігати file_id відправлених файлів для подальшого використання
    file_ids = []

    # Метод 1: BufferedInputFile - для відправки файлів з пам'яті/байтів
    # Для демонстрації BufferedInputFile ми використовуємо "класичне"
    # відкриття файлу через `open()`. Але загалом кажучи,
    # цей метод найкраще підходить для відправки байтів з RAM
    # після виконання деяких маніпуляцій, наприклад, редагування через Pillow
    with open("buffer_emulation.jpg", "rb") as image_from_buffer:
        result = await message.answer_photo(
            BufferedInputFile(
                image_from_buffer.read(),
                filename="image from buffer.jpg"
            ),
            caption="Зображення з буфера"
        )
        file_ids.append(result.photo[-1].file_id)

    # Метод 2: FSInputFile - для відправки файлів безпосередньо з файлової системи
    # Це найпоширеніший метод для локальних файлів
    image_from_pc = FSInputFile("image_from_pc.jpg")
    result = await message.answer_photo(
        image_from_pc,
        caption="Зображення з файлу на комп'ютері"
    )
    file_ids.append(result.photo[-1].file_id)

    # Метод 3: URLInputFile - для відправки файлів з URL
    # Telegram завантажить файл з URL
    image_from_url = URLInputFile("https://picsum.photos/seed/groosha/400/300")
    result = await message.answer_photo(
        image_from_url,
        caption="Зображення через URL"
    )
    file_ids.append(result.photo[-1].file_id)
    
    # Показати всі зібрані file_id для майбутнього використання
    await message.answer("Відправлені файли:\n"+"\n".join(file_ids))


@dp.message(Command("album"))
async def cmd_album(message: Message):
    """
    Обробник команди /album - демонструє відправку медіагруп (альбомів)
    Показує як використовувати MediaGroupBuilder для створення альбомів фото/відео
    """
    # Створення будівельника медіагрупи із загальним підписом
    # Підпис буде показаний під усім альбомом
    album_builder = MediaGroupBuilder(
        caption="Загальний підпис для майбутнього альбому"
    )
    
    # Метод 1: Загальний метод add() - явно вказати тип
    album_builder.add(
        type="photo",
        media=FSInputFile("image_from_pc.jpg")
        # caption="Caption for specific media"  # Індивідуальні підписи опціональні
    )
    
    # Метод 2: Типоспецифічні методи - якщо ми знаємо тип наперед
    # замість загального add() можемо одразу викликати add_<тип>
    album_builder.add_photo(
        # Для посилань або file_id просто вказати значення безпосередньо
        media="https://picsum.photos/seed/groosha/400/300"
    )
    
    # Метод 3: Використання існуючого file_id (найефективніше для повторного використання)
    album_builder.add_photo(
        media="<your file_id>"  # Замінити на справжній file_id з попередніх завантажень
    )
    
    # Відправити медіагрупу - не забути викликати build()!
    await message.answer_media_group(
        media=album_builder.build()
    )


@dp.message(F.text)
async def extract_data(message: Message):
    """
    Обробник будь-якого текстового повідомлення - демонструє витягування сутностей
    Витягує URL, електронні адреси та фрагменти коду з сутностей повідомлення
    Показує правильний спосіб витягування тексту з сутностей
    """
    # Ініціалізація словника даних з значеннями за замовчуванням
    data = {
        "url": "<N/A>",
        "email": "<N/A>",
        "code": "<N/A>"
    }
    
    # Отримання сутностей з повідомлення (може бути None, якщо сутностей немає)
    entities = message.entities or []
    
    # Обробка кожної сутності, знайденої в повідомленні
    for item in entities:
        if item.type in data.keys():
            # НЕПРАВИЛЬНИЙ спосіб (може викликати проблеми з Unicode):
            # data[item.type] = message.text[item.offset : item.offset+item.length]
            
            # ПРАВИЛЬНИЙ спосіб - використання методу extract_from():
            # Цей метод правильно обробляє символи Unicode та кодування
            data[item.type] = item.extract_from(message.text)
    
    # Відправка витягнутих даних назад користувачу
    # Використання html.quote() для безпечного відображення потенційно небезпечного вмісту
    await message.reply(
        "Ось що я знайшов:\n"
        f"URL: {html.quote(data['url'])}\n"
        f"E-mail: {html.quote(data['email'])}\n"
        f"Код: {html.quote(data['code'])}"
    )

@dp.message(F.text)
async def echo_with_time(message: Message):
    """
    Альтернативний обробник тексту - демонструє відлуння повідомлень з міткою часу
    ПРИМІТКА: Цей обробник зараз перевизначений обробником extract_data вище
    Щоб використовувати цей обробник, закоментуйте попередній @dp.message(F.text) обробник
    """
    # Отримання поточного часу в часовому поясі ПК
    time_now = datetime.now().strftime('%H:%M')
    
    # Створення підкресленого тексту з використанням утиліти html.underline()
    added_text = html.underline(f"Створено о {time_now}")
    
    # Відправка нового повідомлення з оригінальним HTML текстом + мітка часу
    # message.html_text зберігає оригінальне форматування
    await message.answer(f"{message.html_text}\n\n{added_text}")


@dp.message(F.animation)
async def echo_gif(message: Message):
    """
    Обробник повідомлень GIF/анімацій - демонструє відлуння анімацій
    Відповідає тією ж анімацією, використовуючи її file_id
    """
    await message.reply_animation(message.animation.file_id)


@dp.message(F.photo)
async def download_photo(message: Message, bot: Bot):
    """
    Обробник повідомлень з фотографіями - демонструє завантаження файлів
    Завантажує фотографію найвищої якості в локальне сховище
    """
    # message.photo[-1] отримує версію фотографії найвищої якості
    # Фотографії зберігаються як масив з різними роздільними здатностями
    await bot.download(
        message.photo[-1],
        destination=f"/tmp/{message.photo[-1].file_id}.jpg"
    )


@dp.message(F.sticker)
async def download_sticker(message: Message, bot: Bot):
    """
    Обробник повідомлень зі стікерами - демонструє завантаження стікерів
    Завантажує стікер у форматі WebP в локальне сховище
    """
    await bot.download(
        message.sticker,
        destination=f"/tmp/{message.sticker.file_id}.webp"
    )


@dp.message(F.new_chat_members)
async def somebody_added(message: Message):
    """
    Обробник нових учасників чату - демонструє події групових чатів
    Спрацьовує, коли хтось приєднується до групи/супергрупи
    """
    # Обробка кожного нового учасника (може бути кілька в одній події)
    for user in message.new_chat_members:
        await message.reply(f"Привіт, {user.full_name}")


async def main():
    """
    Основна функція для запуску бота
    Налаштовує поллінг та обробляє очищення
    """
    # Запуск бота та пропуск всіх накопичених оновлень.
    # Корисно при перезапуску бота, щоб уникнути обробки старих повідомлень.
    # І так, цей метод можна використовувати навіть якщо у вас є поллінг.
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запуск бота в режимі довгого поллінгу
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Запуск основної функції в асинхронному режимі
    # Точка входу в програму
    asyncio.run(main())
