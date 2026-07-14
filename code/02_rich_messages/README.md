# Форматирование сообщений

В этом каталоге исходники к главе https://mastergroosha.github.io/aiogram-3-guide/rich-messages/

## Первый запуск

Установите `uv`, если он ещё не установлен: https://docs.astral.sh/uv/getting-started/installation/

Перейдите в каталог проекта:

```bash
cd code/02_rich_messages
```

Создайте файл настроек из примера:

```bash
cp settings.example.toml settings.toml
```

Откройте `settings.toml` и замените значение `bot.token` на токен вашего бота, полученный у [@BotFather](https://telegram.dog/BotFather).

Синхронизируйте окружение и установите зависимости:

```bash
uv sync
```

Запустите бота:

```bash
uv run python -m bot
```
