from enum import Enum
from typing import TypedDict


RULE_NAME = "server.security.dispatchBrowseAuditMode"

RULE_INTERCEPT_TYPE = "PROP"

RULE_INTERCEPT_METHOD = "riskWebsiteMode"


class RULE_SETTINGS_AUDIT_MODE(Enum):
    DISABLE_AUDIT = "disableAudit"
    BLACK_LIST = "blackList"
    WHITE_LIST = "whiteList"


class RULE_SETTINGS_TYPE(TypedDict):
    enable: bool
    mode: RULE_SETTINGS_AUDIT_MODE


def ruleFunc(config: RULE_SETTINGS_TYPE, param: int) -> int:
    RULE_CONFIG = config
    result = param

    if not RULE_CONFIG["enable"]:
        return result

    match config["mode"]:
        case RULE_SETTINGS_AUDIT_MODE.DISABLE_AUDIT.value:
            result = 0
        case RULE_SETTINGS_AUDIT_MODE.BLACK_LIST.value:
            result = 1
        case RULE_SETTINGS_AUDIT_MODE.WHITE_LIST.value:
            result = 2

    return result
