from typing import Any, Literal
from loguru import logger

import lifecycle

from typeDefs.websocket import wsBasePush
from typeDefs.websocketRoutes.config import UPDATE_CONFIG_RETURN, AuraPLSBaseConfig


def getBasicConfig() -> AuraPLSBaseConfig | None:
    if lifecycle.appConfig == None:
        logger.error("💣 App Config isn't initialized.")
        return None
    return {
        "certPath": lifecycle.appConfig["certPath"],
        "keyPath": lifecycle.appConfig["keyPath"],
        "proxyProcArr": lifecycle.appConfig["proxyProcArr"],
        "wsHost": lifecycle.appConfig["wsHost"],
        "wsPort": lifecycle.appConfig["wsPort"],
    }


def getRuleSettings() -> dict | None:
    if lifecycle.appConfig == None or not lifecycle.appConfig["ruleSettings"]:
        logger.error("💣 Rule Settings isn't initialized.")
        return None
    return {**lifecycle.appConfig["ruleSettings"]}


def pushConfig(type: Literal["basic", "rule"]) -> wsBasePush:
    data = getBasicConfig() if type == "basic" else getRuleSettings()
    pushMetType = (
        "config.action.pushBasicConfig"
        if type == "basic"
        else "config.action.pushRuleSettings"
    )
    if data == None:
        return {"success": False, "data": None, "type": pushMetType}
    else:
        return {"success": True, "data": data, "type": pushMetType}


def updateConfig(target: str, data: Any) -> UPDATE_CONFIG_RETURN:
    targetArr = target.split(".")
    currentConfig = lifecycle.appConfig
    levelIdx = 0
    for levelIdx in range(len(targetArr) - 1):
        level = target[levelIdx]
        isKeyValid = (
            (level in currentConfig) if levelIdx != 0 else hasattr(currentConfig, level)
        )
        if isKeyValid:
            currentConfig = (
                currentConfig[level] if levelIdx != 0 else getattr(currentConfig, level)
            )
            levelIdx += 1
        else:
            return UPDATE_CONFIG_RETURN.KEY_NOT_FOUND

    try:
        currentConfig[targetArr[-1]] = data
        lifecycle.appConfig.saveConfig()
    except:
        return UPDATE_CONFIG_RETURN.UNEXPECTED_ERROR

    return UPDATE_CONFIG_RETURN.SUCCESS
