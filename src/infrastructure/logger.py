from loguru import logger
import sys


def genDynColor(record):
    logLevel = record["level"].name
    levelColors = {
        "INFO": "<bg cyan>+</bg cyan>",
        "ERROR": "<bg red>+</bg red>",
        "WARNING": "<bg yellow><black>+</black></bg yellow>",
        "DEBUG": "<bg white><black>+</black></bg white>",
    }
    color = levelColors.get(logLevel, "<white>+</white>").split("+")
    result = f"<green>[Aura-PLS]</green> <yellow>{{time:YYYY-MM-DD HH:MM:SS}}</yellow> | {color[0]}{{level}}{color[1]} | {{message}}\r\n"
    return result


def setupLogger():
    logger.remove(0)
    logger.add(
        sys.stdout,
        format=genDynColor,
        colorize=True,
    )
    return logger
