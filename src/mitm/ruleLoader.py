from enum import Enum
import importlib

from loguru import logger

import lifecycle


class PACKET_SOFT_METHODS(Enum):
    GET = "GET"
    POST = "POST"
    RPC = "RPC"
    PROP = "PROP"
    UNKNOWN = "UNKNOWN"


def loadRules():
    logger.info("🔁 Trying to load rewrite rules ...")
    rulesPrefix = "mitm.rules"

    ruleSettings = lifecycle.appConfig.ruleSettings
    ruleMapping = lifecycle.ruleMapping
    for direction in ruleSettings:
        logger.debug(f"♐ Loading rules for direction: {direction} ...")
        if not (direction in ruleMapping):
            ruleMapping[direction] = {}
            for type in PACKET_SOFT_METHODS:
                ruleMapping[direction][type.value] = {}
        for ruleCategory in ruleSettings[direction]:
            logger.debug(f"✳️ Loading rule category: {direction}.{ruleCategory}")
            baseInfo = importlib.import_module(
                ".".join([rulesPrefix, direction, ruleCategory, "__base__"])
            )
            for perRule in ruleSettings[direction][ruleCategory]:
                moduleId = ".".join([direction, ruleCategory, perRule])
                logger.info(f"❇️ Registering rule: {moduleId}")
                targetModulePath = f"{rulesPrefix}.{moduleId}"
                logger.debug(f"🧊 Expected module path: {targetModulePath}")
                ruleModule = importlib.import_module(targetModulePath)

                if (
                    ruleModule.RULE_INTERCEPT_TYPE in PACKET_SOFT_METHODS
                    and ruleModule.RULE_INTERCEPT_METHOD
                ):
                    ruleObject = {
                        "name": ruleModule.RULE_NAME,
                        "ruleFunc": ruleModule.ruleFunc,
                        "config": baseInfo.RULE_CONFIG_BASE[perRule],
                    }

                    # use try - except instead of hasattr
                    # because hasattr is unfriendly to performance
                    try:
                        ruleMapping[direction][ruleModule.RULE_INTERCEPT_TYPE][
                            ruleModule.RULE_INTERCEPT_METHOD
                        ].append(ruleObject)
                    except KeyError:
                        ruleMapping[direction][ruleModule.RULE_INTERCEPT_TYPE][
                            ruleModule.RULE_INTERCEPT_METHOD
                        ] = [ruleObject]

                    logger.info("🎯 Done.")
                else:
                    logger.warning("⛔ Rule validation failed, skipping ...")

    logger.success("✅ Finished rules registration.")
    logger.debug("🪢 Current ruleMapping:")
    logger.debug(ruleMapping)
