import logging
import logging.config
import re
import sys
from typing import Literal, Optional

import click

from . import config

name = "gci1004"
logger = logging.getLogger(name)


def init_logging() -> None:
    "Configures the logger."

    current_loggers = logging.Logger.manager.loggerDict.keys()  # type: ignore

    logging.config.dictConfig(
        {
            "disable_existing_loggers": True,
            "formatters": {
                "simple": {
                    "format": "%(levelname)s - %(message)s",
                    "class": "src.logging.ColourFormatter",
                },
                "complete": {
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "format": "%(asctime)s - "
                    "%(name)s - "
                    "%(levelname)s - "
                    "%(message)s",
                },
            },
            "filters": {"route": {"()": RouteFilter}},
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "simple",
                    "stream": "ext://sys.stdout",
                    "level": "DEBUG" if config.DEBUG else "INFO",
                    "filters": ["route"],
                },
            },
            "loggers": {
                **{
                    logger: {
                        "handlers": ["console"],
                        "level": "WARNING",
                        "propagate": False,
                    }
                    for logger in current_loggers
                },
                **{
                    name: {
                        "handlers": ["console"],
                        "level": "DEBUG" if config.DEBUG else "INFO",
                        "propagate": True,
                    },
                    "uvicorn.access": {
                        "handlers": ["console"],
                        "level": "INFO",
                        "propagate": False,
                    },
                },
            },
            "version": 1,
        }
    )


class ColourFormatter(logging.Formatter):  # pragma: no cover
    level_name_colours = {
        logging.DEBUG: lambda level: click.style(str(level), fg="cyan"),
        logging.INFO: lambda level: click.style(str(level), fg="green"),
        logging.WARNING: lambda level: click.style(str(level), fg="yellow"),
        logging.ERROR: lambda level: click.style(str(level), fg="red"),
        logging.CRITICAL: lambda level: click.style(
            str(level), fg="bright_red"
        ),
    }

    def __init__(
        self: "ColourFormatter",
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: Literal["%", "{", "$"] = "%",
        use_colours: Optional[bool] = None,
    ) -> None:
        if use_colours in (True, False):
            self.use_colours = use_colours  # pragma: no cover
        else:
            self.use_colours = sys.stdout.isatty()
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def colour_level_name(
        self: "ColourFormatter", level_name: str, level_no: int
    ) -> str:
        fct = self.level_name_colours.get(
            level_no,
            lambda level_name: str(  # pylint: disable=unnecessary-lambda
                level_name
            ),
        )  # pragma: no cover
        return fct(level_name)  # pragma: no cover

    def formatMessage(
        self: "ColourFormatter", record: logging.LogRecord
    ) -> str:
        if self.use_colours:
            record.levelname = self.colour_level_name(
                record.levelname, record.levelno
            )  # pragma: no cover
        return super().formatMessage(record)


class RouteFilter(logging.Filter):
    def __init__(self: "RouteFilter", *args: str, **kwargs: str) -> None:
        super().__init__(*args, **kwargs)

    def filter(self: "RouteFilter", record: logging.LogRecord) -> bool:
        routes = [
            "/ping",
            "/",
            "/static/scripts/.+.js",
            "/static/styles/.+.css",
        ]
        msg = record.getMessage()
        return all(
            re.search(f'"GET {route}(?:\\?\\S+)? HTTP/1.1" 200', msg) is None
            for route in routes
        )
