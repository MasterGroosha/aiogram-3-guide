import tomllib
from enum import StrEnum
from pathlib import Path
from typing import Any, Tuple, Type

from pydantic import BaseModel, SecretStr
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class LogRenderer(StrEnum):
    JSON = "json"
    CONSOLE = "console"


class BotConfig(BaseModel):
    token: SecretStr


class LogConfig(BaseModel):
    project_name: str
    show_datetime: bool
    datetime_format: str
    show_debug_logs: bool
    time_in_utc: bool
    use_colors_in_console: bool
    renderer: LogRenderer
    allow_third_party_logs: bool


class TomlConfigSettingsSource(PydanticBaseSettingsSource):
    """
    Источник для чтения настроек из TOML-файла.
    В этой версии подразумевается, что файл settings.toml
    находится в корневой директории проекта, рядом с пакетом bot.
    """

    def get_field_value(
        self, field: Any, field_name: str
    ) -> Tuple[Any, str, bool]:
        return None, field_name, False

    def __call__(self) -> dict[str, Any]:
        file_path = Path(__file__).resolve().parent.parent.joinpath("settings.toml")
        if not file_path.exists():
            return {}
        with file_path.open("rb") as f:
            return tomllib.load(f)


class Settings(BaseSettings):
    # Перечисляем, какие ключи ожидаются в конфиге
    bot: BotConfig
    logs: LogConfig

    """
    Задаём параметры чтения конфига:
    1. Разделитель вложенных ключей при чтении переменных окружения __
    Т.е. ключ token внутри секции bot будет ожидаться как BOT__TOKEN
    2. extra="ignore" - игнорируем любые ключи, которые не описаны в конфиге
    """
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        extra="ignore",
    )

    # Этот кусок можно просто копипастить, он задаёт порядок чтения настроек.
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            TomlConfigSettingsSource(settings_cls),
        )
