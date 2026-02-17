import logging
from json import dumps
from sys import stdout

import structlog
from structlog import WriteLoggerFactory

from .config_reader import LogConfig, LogRenderer


def get_structlog_config(log_config: LogConfig) -> dict:
    if log_config.show_debug_logs is True:
        min_level = logging.DEBUG
    else:
        min_level = logging.INFO

    if log_config.allow_third_party_logs:
        # Create handler for stdlib logging
        standard_handler = logging.StreamHandler(stream=stdout)
        standard_handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                processors=get_processors(log_config)
            )
        )

        # Configure root logger to use this handler
        standard_logger = logging.getLogger()
        standard_logger.addHandler(standard_handler)
        standard_logger.setLevel(logging.DEBUG if log_config.show_debug_logs else logging.INFO)


    return {
        "processors": get_processors(log_config),
        "cache_logger_on_first_use": True,
        "wrapper_class": structlog.make_filtering_bound_logger(min_level),
        "logger_factory": WriteLoggerFactory()
    }


def get_processors(log_config: LogConfig) -> list:
    def custom_json_serializer(data, *args, **kwargs):
        result = dict()

        # Set keys in specific order
        for key in ("level", "event"):
            if key in data:
                result[key] = data.pop(key)

        # Clean up non-native structlog logs:
        if "_from_structlog" in data:
            data.pop("_from_structlog")
            data.pop("_record")

        # Add all other fields
        result.update(**data)
        return dumps(result, default=str)

    def custom_console_serializer(logger, method_name: str, event_dict: dict) -> dict:
        """Remove structlog internal keys from event_dict"""
        if "_from_structlog" in event_dict:
            event_dict.pop("_from_structlog")
            event_dict.pop("_record")
        return event_dict

    def add_source_info(logger, method_name: str, event_dict: dict) -> dict:
        """Add source information: app vs third-party"""
        if "_record" in event_dict:
            # This is a stdlib log (third-party library)
            record = event_dict["_record"]
            event_dict["source"] = f"{record.name}"
        else:
            # This is a structlog log (our app)
            event_dict["source"] = "app"
        return event_dict

    processors = list()
    if log_config.show_datetime is True:
        processors.append(structlog.processors.TimeStamper(
            fmt=log_config.datetime_format,
            utc=log_config.time_in_utc
            )
        )

    processors.append(structlog.processors.add_log_level)

    if log_config.allow_third_party_logs:
        processors.append(add_source_info)

    if log_config.renderer == LogRenderer.JSON:
        processors.append(structlog.processors.JSONRenderer(serializer=custom_json_serializer))
    else:
        processors.append(custom_console_serializer)
        processors.append(structlog.dev.ConsoleRenderer(
            colors=log_config.use_colors_in_console,
            pad_level=False
        ))
    return processors
