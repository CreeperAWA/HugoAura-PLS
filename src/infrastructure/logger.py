import inspect
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


def setupLogger(debug: bool):
    logger.remove(0)
    logger.add(
        sys.stdout,
        format=genDynColor,
        colorize=True,
        level="DEBUG" if debug else "INFO",
    )
    lifecycle.loggerInstance = logger
    return logger
