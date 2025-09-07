# Читання конфігурації для налаштувань бота
from pydantic import SecretStr                                    # Для безпечного зберігання токену
from pydantic_settings import BaseSettings, SettingsConfigDict   # Управління налаштуваннями


class Settings(BaseSettings):
    """
    Налаштування конфігурації бота
    Читає значення зі змінних середовища або файлу .env
    """
    bot_token: SecretStr    # Токен Telegram бота (зберігається в безпеці)

    # Конфігурація для читання з файлу .env з кодуванням UTF-8
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


# Глобальний екземпляр конфігурації
config = Settings()