from loguru import logger
from mitm.ruleLoader import PACKET_SOFT_METHODS
import lifecycle


GET_PACKET_CACHE = {}


def determinePacketSoftMethod(topic: str) -> PACKET_SOFT_METHODS:
    if "/thing/post" in topic:
        return PACKET_SOFT_METHODS.POST
    elif "/rpc/" in topic:
        return PACKET_SOFT_METHODS.RPC
    elif "/up/request" in topic or "/up/response" in topic:
        return PACKET_SOFT_METHODS.GET
    else:
        return PACKET_SOFT_METHODS.UNKNOWN


def handlePublishPacket(resolvedSinglePacket: dict, topic: str, isClient: bool) -> dict:
    noRewrite = True
    packetSoftMethod = determinePacketSoftMethod(topic)
    direction = "server" if not isClient else "client"
    try:
        method = resolvedSinglePacket["method"]
    except KeyError:
        method = None

    if packetSoftMethod.value == PACKET_SOFT_METHODS.GET:
        ascendId = topic.split("/")[-1]
        if direction == "client":
            GET_PACKET_CACHE[ascendId] = resolvedSinglePacket["method"]
        elif direction == "server":
            try:
                resolvedSinglePacket["method"] = GET_PACKET_CACHE[ascendId]
            except KeyError:
                resolvedSinglePacket["method"] = ""

    result = resolvedSinglePacket

    if method != None and (direction in lifecycle.ruleMapping):
        if resolvedSinglePacket["method"] in [
            "thing.property.set",
            "thing.property.get",
        ]:
            params = resolvedSinglePacket["params"].keys()
            for key in params:
                try:
                    targetRules = lifecycle.ruleMapping[direction][
                        PACKET_SOFT_METHODS.PROP
                    ][key]
                    for rule in targetRules:
                        ret = rule["ruleFunc"](rule["config"], result["params"][key])
                        if ret != None:
                            result["params"][key] = ret
                            continue
                    noRewrite = False
                except KeyError:
                    continue  # Do nothing, cause of no corresponding rule
                except Exception as e:
                    logger.critical(
                        f"💥 Unexpected error occurred processing {PACKET_SOFT_METHODS.PROP.value}::{key}, error:\r\n{e}"
                    )

            if lifecycle.isDebug:
                logger.debug(
                    f"🏅 Successfully processed {PACKET_SOFT_METHODS.PROP.value} packet with params {params}\r\n--- Result ---\r\n{result}"
                )
        else:
            try:
                targetRules = lifecycle.ruleMapping[direction][packetSoftMethod.value][
                    resolvedSinglePacket["method"]
                ]
                for rule in targetRules:
                    ret = rule["ruleFunc"](rule["config"], result)
                    if ret != None:
                        result = ret
                        continue  # 允许一次 packet 叠加多类修改
                noRewrite = False

                if lifecycle.isDebug:
                    logger.debug(
                        f"🏅 Successfully processed packet with method {resolvedSinglePacket["method"]}\r\n--- Result ---\r\n{result}"
                    )
            except KeyError:
                pass
            except Exception as e:
                logger.critical(
                    f"💥 Unexpected error occurred processing {resolvedSinglePacket["method"]}, error:\r\n{e}"
                )

    return {"result": result, "noRewrite": noRewrite}
