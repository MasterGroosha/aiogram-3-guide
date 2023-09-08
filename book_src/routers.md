---
title: Роутеры, многофайловость и структура бота
description: Роутеры, многофайловость и структура бота
---

# Роутеры, многофайловость и структура бота

!!! info ""
    Используемая версия aiogram: 3.0

В этой главе мы познакомимся с новой фичей aiogram 3.x — роутерами, научимся разбивать наш код на отдельные 
компоненты, а также сформируем базовую структуру бота, которая пригодится в следующих главах и вообще по жизни.

## Точка входа в приложение {: id="entrypoint" }

Театр начинается с вешалки, а бот начинается с точки входа. Пусть это будет файл `bot.py`. В нём мы определим 
асинхронную функцию `main()`, в которой создадим необходимые объекты и запустим поллинг. Какие 
объекты являются необходимыми? Во-первых, разумеется, бот. Их может быть несколько, но об этом 
как-нибудь в другой раз. Во-вторых, диспетчер. Он занимается приёмом событий от Telegram и раскидыванием их 
по хэндлерам через фильтры и мидлвари.

```python title="bot.py"
import asyncio
from aiogram import Bot, Dispatcher


# Запуск бота
async def main():
    bot = Bot(token="TOKEN")
    dp = Dispatcher()

    # Запускаем бота и пропускаем все накопленные входящие
    # Да, этот метод можно вызвать даже если у вас поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
```

Но чтобы обрабатывать сообщения, этого недостаточно, нужны ещё хэндлеры. Мы хотим их расположить 
в других файлах, чтобы не устраивать портянки на несколько тысяч строк. В предыдущих главах все 
наши хэндлеры прицеплялись к диспетчеру, но сейчас он внутри функции и мы точно не хотим 
делать его глобальным объектом.  
Что же делать? И тут на помощь приходят...

## Роутеры {: id="routers" }

Обратимся к [официальной документации](https://docs.aiogram.dev/en/dev-3.x/dispatcher/router.html) 
aiogram 3.x и посмотрим на следующее изображение: 

![Несколько роутеров](https://docs.aiogram.dev/en/dev-3.x/_images/nested_routers_example.png)

Что мы видим? 

1. Диспетчер — корневой роутер.
2. Хэндлеры цепляются к роутерам.
3. Роутеры могут быть вложенными, но между ними только однонаправленная связь.
4. Порядок включения (и, соответственно, проверки) роутеров явно определён.

На следующем изображении виден порядок поиска апдейтом нужного хэндлера для выполнения:

![порядок поиска апдейтом нужного хэндлера](https://docs.aiogram.dev/en/dev-3.x/_images/update_propagation_flow.png)

Напишем простенького бота с двумя фичами:

1. Если боту отправили `/start`, он должен прислать вопрос и две кнопки с текстами «Да» и «Нет».
2. Если боту прислали любой другой текст, стикер или гифку, он должен ответить названием типа сообщения.

Начнём с клавиатуры: создадим рядом с файлом `bot.py` каталог `keyboards`, а внутри него файл `for_questions.py` 
и напишем функцию для получения простой клавиатуры с кнопками "Да" и "Нет" в один ряд:

```python title="keyboards/for_questions.py"
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_yes_no_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Да")
    kb.button(text="Нет")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)
```

Ничего сложного, тем более, что мы клавиатуры подробно разбирали [ранее](buttons.md). 
Теперь рядом с файлом `bot.py` создадим другой каталог `handlers`, а внутри него файл `questions.py`.

```python title="handlers/questions.py" hl_lines="7 9"
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.for_questions import get_yes_no_kb

router = Router()  # [1]

@router.message(Command("start"))  # [2]
async def cmd_start(message: Message):
    await message.answer(
        "Вы довольны своей работой?",
        reply_markup=get_yes_no_kb()
    )

@router.message(F.text.lower() == "да")
async def answer_yes(message: Message):
    await message.answer(
        "Это здорово!",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(F.text.lower() == "нет")
async def answer_no(message: Message):
    await message.answer(
        "Жаль...",
        reply_markup=ReplyKeyboardRemove()
    )
```

Обратим внимание на пункты [1] и [2]. Во-первых, мы в файле создали свой собственный роутер уровня модуля, и далее 
будем цеплять его к корневому роутеру (диспетчеру). Во-вторых, хэндлеры «отпочковываются» уже от локального роутера.

Аналогичным образом сделаем второй файл с хэндлерами `different_types.py`, где просто будем выводить тип сообщения:

```python title="handlers/different_types.py"
from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text)
async def message_with_text(message: Message):
    await message.answer("Это текстовое сообщение!")

@router.message(F.sticker)
async def message_with_sticker(message: Message):
    await message.answer("Это стикер!")

@router.message(F.animation)
async def message_with_gif(message: Message):
    await message.answer("Это GIF!")

```

Наконец, вернёмся к нашему `bot.py`, импортируем файлы с роутерами и хэндлерами, и подключим их к диспетчеру:

```python title="bot.py" hl_lines="3 11 12"
import asyncio
from aiogram import Bot, Dispatcher
from handlers import questions, different_types


# Запуск бота
async def main():
    bot = Bot(token="TOKEN")
    dp = Dispatcher()

    dp.include_routers(questions.router, different_types.router)

    # Альтернативный вариант регистрации роутеров по одному на строку
    # dp.include_router(questions.router)
    # dp.include_router(different_types.router)

    # Запускаем бота и пропускаем все накопленные входящие
    # Да, этот метод можно вызвать даже если у вас поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
```

Мы просто импортируем файлы из каталога `handlers/` и подключаем роутеры из этих файлов к диспетчеру. И здесь снова 
важен порядок импортов! Если мы поменяем местами регистрацию роутеров, то на команду `/start` бот будет отвечать 
фразой «Это текстовое сообщение!», поскольку функция `message_with_text()` первой успешно пройдёт все фильтры. Но 
о самих фильтрах мы поговорим чуть позже, а пока рассмотрим ещё один вопрос.


## Итог {: id="conclusion" }

У нас получилось аккуратно разделить бота по разным файлам, не нарушая его работу. Примерное дерево файлов 
и каталогов получилось следующим (здесь сознательно пропущены некоторые несущественные для примера файлы):

```
├── bot.py
├── handlers
│   ├── different_types.py
│   └── questions.py
├── keyboards
│   └── for_questions.py
```

В дальнейшем мы будем придерживаться такой структуры, плюс добавятся новые каталоги для фильтров, мидлварей, 
файлов для работы с базами данных и т.д.