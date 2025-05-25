from enum import Enum
from typing import TypedDict
from loguru import logger


RULE_NAME = "client.security.uploadFreezeInfo"

RULE_INTERCEPT_TYPE = "POST"

RULE_INTERCEPT_METHOD = "thing.event.freezeDiskInfo.post"


class RULE_SETTINGS_REWRITE_MODE(Enum):
    ALL_FREEZE = "allFreeze"  # 全部冻结
    ONLY_SYS = "systemOnly"  # 仅系统盘冻结
    EXCEPT_2ND = "exceptSecondDisk"  # 仅第二个磁盘解冻 (如果存在的话)


class RULE_SETTINGS_TYPE(TypedDict):
    rewriteMode: RULE_SETTINGS_REWRITE_MODE


def ruleFunc(config: dict, packet: dict) -> dict:
    RULE_CONFIG = config
    result = packet

    if not RULE_CONFIG["enable"]:
        return result

    diskInfoList = result["params"]["diskInfoList"]
    match RULE_CONFIG["rewriteMode"]:
        case RULE_SETTINGS_REWRITE_MODE.ALL_FREEZE.value:
            for disk in diskInfoList:
                disk["protectedStatus"] = 1
        case RULE_SETTINGS_REWRITE_MODE.ONLY_SYS.value:
            diskInfoList[0]["protectedStatus"] = 1
        case RULE_SETTINGS_REWRITE_MODE.EXCEPT_2ND.value:
            for i in range(len(diskInfoList)):
                if i != 1:
                    diskInfoList[i]["protectedStatus"] = 1
                else:
                    diskInfoList[i]["protectedStatus"] = 0
        case _:
            logger.warning(
                f'Invalid setting {{"rewriteMode": "{RULE_CONFIG["rewriteMode"]}"}} for {RULE_NAME}'
            )

    return result
