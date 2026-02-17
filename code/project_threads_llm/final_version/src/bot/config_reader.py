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
    show_datetime: bool
    datetime_format: str
    show_debug_logs: bool
    time_in_utc: bool
    use_colors_in_console: bool
    renderer: LogRenderer
    allow_third_party_logs: bool


class LLMConfig(BaseModel):
    url: str


class TomlConfigSettingsSource(PydanticBaseSettingsSource):
    """Settings source that reads from a TOML file."""

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
    bot: BotConfig
    logs: LogConfig
    llm: LLMConfig

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        extra="ignore",
        populate_by_name=True,
    )

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
