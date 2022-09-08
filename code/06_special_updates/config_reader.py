from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr
    main_chat_id: int

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


config = Settings()
