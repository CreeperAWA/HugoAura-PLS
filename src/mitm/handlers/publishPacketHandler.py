from loguru import logger
from mitm.ruleLoader import PACKET_SOFT_METHODS
import lifecycle


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
    result = resolvedSinglePacket
    packetSoftMethod = determinePacketSoftMethod(topic)
    direction = "server" if not isClient else "client"
    try:
        method = resolvedSinglePacket["method"]
    except KeyError:
        method = None

    if method != None and (direction in lifecycle.ruleMapping):
        if (
            resolvedSinglePacket["method"]
            in lifecycle.ruleMapping[direction][packetSoftMethod.value]
        ):
            target = lifecycle.ruleMapping[direction][packetSoftMethod.value][
                resolvedSinglePacket["method"]
            ]
            result = target["ruleFunc"](target["config"], resolvedSinglePacket)
            noRewrite = False
            logger.debug(
                f"🏅 Successfully processed packet with method {resolvedSinglePacket["method"]}\r\n--- Result ---\r\n{result}"
            )

    return {"result": result, "noRewrite": noRewrite}
