from datetime import datetime
import os
from pathlib import Path
from loguru import logger
import sys

import lifecycle


def genDynColor(record):
    logLevel = record["level"].name
    levelColors = {
        "INFO": "<bg cyan>+</bg cyan>",
        "ERROR": "<bg red>+</bg red>",
        "WARNING": "<bg yellow><black>+</black></bg yellow>",
        "DEBUG": "<bg white><black>+</black></bg white>",
        "SUCCESS": "<bg green>+</bg green>",
    }
    color = levelColors.get(logLevel, "<white>+</white>").split("+")
    result = f"<green>[Aura-PLS]</green> <yellow>{{time:YYYY-MM-DD hh:mm:ss}}</yellow> | {color[0]}{{level}}{color[1]} | {{message}}\r\n"
    return result


def setupLogger(debug: bool, serviceMode: bool):
    logger.remove(0)
    if not serviceMode:
        logger.add(
            sys.stdout,
            format=genDynColor,
            colorize=True,
            level="DEBUG" if debug else "INFO",
        )

    datetimeIns = datetime.now()
    logDir = Path.joinpath(
        lifecycle.plsDataDir,
        "logs",
    )
    logger.add(
        Path.joinpath(
            logDir,
            f"PLS-{"Service" if serviceMode else "CLI"}-{datetimeIns.year}-{str(datetimeIns.month).zfill(2)}-{str(datetimeIns.day).zfill(2)}-{str(datetimeIns.hour).zfill(2)}-{str(datetimeIns.minute).zfill(2)}-{str(datetimeIns.second).zfill(2)}.log",
        ),
        level="DEBUG" if debug else "INFO",
    )

    lifecycle.loggerInstance = logger
    return logger
