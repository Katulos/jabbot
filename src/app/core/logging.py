import logging
import sys
from collections.abc import Callable
from typing import Any, cast

import orjson
import structlog
from structlog.typing import EventDict, Processor


def _orjson_dumps(v: Any, *, default: Callable[[Any], Any] | None) -> str:
    return cast(str, orjson.dumps(v, default=default).decode())


def _rename_event_field(_, __, event_dict: EventDict) -> EventDict:
    if "msg" in event_dict:
        event_dict["event"] = event_dict.pop("msg")
    return event_dict


def setup_logger(
    loglevel: int = logging.INFO,
    *,
    event_width: int = 50,
) -> None:
    def _format_message(_: Any, __: str, event_dict: EventDict) -> EventDict:
        if "event" in event_dict:
            event_dict["event"] = event_dict["event"].ljust(event_width)
        return event_dict

    base_processors: list[Processor] = [
        structlog.stdlib.add_log_level,
    ]

    foreign_processors = [
        _rename_event_field,
    ]

    structlog.configure(
        processors=base_processors
        + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
        context_class=dict,
        wrapper_class=structlog.stdlib.BoundLogger,
    )

    if sys.stderr.isatty():
        console_processors = (
            base_processors + [_format_message] + foreign_processors
        )
        processors = [
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.dev.ConsoleRenderer(),
        ]
    else:
        console_processors = base_processors + foreign_processors
        processors = [
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.TimeStamper(fmt=None, utc=True),
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(serializer=_orjson_dumps),
        ]

    handler = logging.StreamHandler()
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=console_processors,
            processors=processors,
        ),
    )

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(loglevel)
