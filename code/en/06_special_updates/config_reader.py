# Configuration reader for bot settings
from pydantic import SecretStr                                    # For secure token handling
from pydantic_settings import BaseSettings, SettingsConfigDict   # Settings management


class Settings(BaseSettings):
    """
    Bot configuration settings
    Reads values from environment variables or .env file
    """
    bot_token: SecretStr    # Telegram bot token (kept secret)
    main_chat_id: int       # Main chat ID for admin operations

    # Configuration for reading from .env file with UTF-8 encoding
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


# Global configuration instance
config = Settings()