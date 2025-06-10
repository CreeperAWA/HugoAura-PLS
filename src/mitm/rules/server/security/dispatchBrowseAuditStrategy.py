from enum import Enum
from typing import TypedDict


RULE_NAME = "server.security.dispatchBrowseAuditStrategy"

RULE_INTERCEPT_TYPE = "RPC"

RULE_INTERCEPT_METHOD = "thing.service.updateBrowseAuditStrategy"


class RULE_SETTINGS_STRATEGY_TYPE(Enum):
    BLACK_LIST_MODE = "blackList"
    WHITE_LIST_MODE = "whiteList"


class RULE_SETTINGS_TYPE(TypedDict):
    enable: bool
    strategyType: RULE_SETTINGS_STRATEGY_TYPE
    allowSites: list[str]
    forbiddenSites: list[str]


def ruleFunc(config: RULE_SETTINGS_TYPE, packet: dict) -> dict:
    RULE_CONFIG = config
    result = packet

    if not RULE_CONFIG["enable"]:
        return result

    result["params"]["strategyType"] = RULE_CONFIG["strategyType"]
    result["params"]["strategy"]["allow"] = RULE_CONFIG["allowSites"]
    result["params"]["strategy"]["forbidden"] = RULE_CONFIG["forbiddenSites"]

    return result
