import logging
from json import dumps

import structlog
from structlog import WriteLoggerFactory

from bot.config_reader import LogConfig, LogRenderer


def get_structlog_config(
    log_config: LogConfig
) -> dict:
    """
    Получение конфигурации для structlog
    :param log_config: объект LogConfig с параметрами логирования
    :return: словарь с конфигурацией structlog
    """

    # Показывать или нет логи уровня debug
    if log_config.show_debug_logs is True:
        min_level = logging.DEBUG
    else:
        min_level = logging.INFO

    return {
        "processors": get_processors(log_config),
        "cache_logger_on_first_use": True,
        "wrapper_class": structlog.make_filtering_bound_logger(min_level),
        "logger_factory": WriteLoggerFactory()
    }


def get_processors(log_config: LogConfig) -> list:
    """
    Возвращает список процессоров для structlog
    :param log_config: объект LogConfig с параметрами логирования
    :return: список процессоров для structlog
    """
    def custom_json_serializer(data, *args, **kwargs):
        """
        Кастомный сериализатор для JSON-логов
        """
        result = dict()


        if log_config.show_datetime is True:
            result["timestamp"] = data.pop("timestamp")

        # Все остальные следующие два ключа идут именно в таком порядке
        for key in ("level", "event"):
            if key in data:
                result[key] = data.pop(key)

        # Все остальные ключи выводятся "как есть"
        # (обычно в алфавитном порядке)
        result.update(**data)
        return dumps(result, default=str)

    processors = list()

    # В некоторых случаях не нужно выводить отметку времени,
    # поскольку она уже добавляется вышестоящим сервисом, например, systemd
    if log_config.show_datetime is True:
        processors.append(structlog.processors.TimeStamper(
            fmt=log_config.datetime_format,
            utc=log_config.time_in_utc
            )
        )

    # Всегда добавляем уровень лога
    processors.append(structlog.processors.add_log_level)

    # Выбор рендера: JSON или для вывода в терминал
    if log_config.renderer == LogRenderer.JSON:
        processors.append(structlog.processors.JSONRenderer(serializer=custom_json_serializer))
    else:
        processors.append(structlog.dev.ConsoleRenderer(
            # Можно отключить цвета в логах
            colors=log_config.use_colors_in_console,
            # Можно убрать паддинг в уровнях, т.е. вместо
            # [info   ] Some info log
            # [warning] Some warning log
            # будет
            # [info] Some info log
            # [warning] Some warning log
            pad_level=True
        ))
    return processors
