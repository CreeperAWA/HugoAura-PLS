# 人生中第一次手写 TCP 包的解析 (((> <)))
from base64 import encode
import json
from loguru import logger
from mitmproxy.tcp import TCPMessage

from mitm.handlers.publishPacketHandler import handlePublishPacket
import lifecycle
from typeDefs.mqtt import MQTT_PACKET_TYPES


splitPacketPoolClient = []
splitPacketPoolServer = []


def validatePackage(msg: bytes, pendingArr: list[dict], isClient: bool):
    targetCacheArr = splitPacketPoolClient if isClient else splitPacketPoolServer
    isCacheAreaClean = len(targetCacheArr) == 0
    isIncomingPktMiddle = (
        targetCacheArr[-1]["remainLength"] > len(msg)
        if isCacheAreaClean != True
        else False
    )
    pointer = 0
    shouldStop = False

    if isIncomingPktMiddle:
        logger.debug(
            f"⚠ Middle package detected ⚠\r\n--- Middle packet content ---\r\n{msg}"
        )
        targetCacheArr.append(
            {
                "packet": msg,
                "length": targetCacheArr[-1]["length"],
                "type": targetCacheArr[-1]["type"],
                "beginOfMutableHeader": None,
                "id": len(splitPacketPoolClient) + 1,
                "remainLength": targetCacheArr[-1]["remainLength"] - len(msg),
            }
        )
        return pendingArr

    def runCheck(pointer: int) -> dict:
        noContinueRep = {"continue": False, "nextTick": None, "curPacketLength": None}
        if pointer + 1 >= len(msg):
            return noContinueRep
        packetType = determinePacketType(msg, pointer)
        if packetType != MQTT_PACKET_TYPES.UNKNOWN:
            packetLength = calcLength(msg, pointer + 1)
            nextTick = packetLength["nextTick"] + packetLength["length"]
            packet = msg[pointer:nextTick]
            return {
                "continue": True,
                "nextTick": nextTick,
                "curPacketLength": packetLength["length"],
                "packet": packet,
                "type": packetType.value,
                "beginOfMutableHeader": packetLength["nextTick"] - pointer,
            }
        else:
            return noContinueRep

    def genPacketFromCache(targetCacheArr: list) -> dict:
        fullMsg: bytes = b""
        for singlePkt in targetCacheArr:
            fullMsg += singlePkt["packet"]
        return {
            "packet": fullMsg,
            "length": targetCacheArr[-1]["length"],
            "type": targetCacheArr[-1]["type"],
            "beginOfMutableHeader": targetCacheArr[0]["beginOfMutableHeader"],
        }

    if not isCacheAreaClean:
        pointer += targetCacheArr[-1]["remainLength"]
        targetCacheArr.append(
            {
                "packet": msg[0:pointer],
                "length": targetCacheArr[-1]["length"],
                "type": targetCacheArr[-1]["type"],
                "id": len(targetCacheArr) + 1,
                "remainLength": 0,
            }
        )
        fullPendingMsg = genPacketFromCache(targetCacheArr)
        pendingArr.append(fullPendingMsg)
        targetCacheArr.clear()
        logger.debug(
            f"🔗 Successfully merged packet\r\n--- 🛠️ Merged packet ---\r\n{fullPendingMsg["packet"]}"
        )

    while shouldStop == False:
        result = runCheck(pointer)
        if result["nextTick"] != None:
            pointer = result["nextTick"]
        if result["continue"]:
            pendingArr.append(
                {
                    "packet": result["packet"],
                    "length": result["curPacketLength"],
                    "type": result["type"],
                    "beginOfMutableHeader": result["beginOfMutableHeader"],
                }
            )
        else:
            # 确认一下这个包有没有结束
            if len(msg) < pointer:  # pointer 不需要 - 1, 因为 pointer 是 index
                logger.debug("⚠ Split package detected ⚠")
                incompletePacket = pendingArr.pop()
                targetCacheArr.append(
                    {
                        **incompletePacket,
                        "id": len(targetCacheArr) + 1,
                        "remainLength": pointer - len(msg),
                    }
                )

            shouldStop = True

    return pendingArr


def determinePacketType(msg: bytes, idx=0) -> MQTT_PACKET_TYPES:
    # 不用 match case, 因为需要范围比较
    firstByte = msg[idx]
    if firstByte == 16:
        return MQTT_PACKET_TYPES.CONNECT
    elif firstByte == 32:
        return MQTT_PACKET_TYPES.CONNACK
    elif 48 <= firstByte <= 63:
        return MQTT_PACKET_TYPES.PUBLISH
    elif firstByte == 64:
        return MQTT_PACKET_TYPES.PUBACK
    elif 128 <= firstByte <= 130:
        return MQTT_PACKET_TYPES.SUBSCRIBE
    elif firstByte == 144:
        return MQTT_PACKET_TYPES.SUBACK
    elif 160 <= firstByte <= 162:
        return MQTT_PACKET_TYPES.UNSUBSCRIBE
    elif firstByte == 176:
        return MQTT_PACKET_TYPES.UNSUBACK
    elif firstByte == 192:
        return MQTT_PACKET_TYPES.PINGREQ
    elif firstByte == 208:
        return MQTT_PACKET_TYPES.PINGRESP
    elif firstByte == 224:
        return MQTT_PACKET_TYPES.DISCONN
    else:
        return MQTT_PACKET_TYPES.UNKNOWN


def determineControls(msg: bytes) -> dict:
    firstByte = msg[0]
    firstBin = bin(firstByte)[2:].zfill(8)
    isDup = False if firstBin[4] == "0" else True
    qos = int(firstBin[5 : 6 + 1], 2)
    isRetain = False if firstBin[-1] == "0" else True
    return {"isDup": isDup, "qos": qos, "isRetain": isRetain}


def calcLength(msg: bytes, baseline=1) -> dict:
    totalLength = 0
    multiplier = 1
    bytesUsed = 0

    for i in range(baseline, min(baseline + 4, len(msg))):
        byte = msg[i]
        totalLength += (byte & 0x7F) * multiplier
        bytesUsed += 1
        if byte & 0x80 == 0:
            return {"length": totalLength, "nextTick": i + 1}
        multiplier *= 128

    raise ValueError


def resolvePublishPacket(
    msg: bytes, initPointer: int, _messageTotalLength: int, controls: dict
) -> dict:
    topicLength = (
        msg[initPointer] + msg[initPointer + 1]
    )  # 可变 Header 的前两字节是 Topic 长度
    topicStartPoint = initPointer + 2
    topicEndPoint = topicStartPoint + topicLength - 1  # 虽然 - 1 毫无意义, 但方便理解 (
    topic = ""
    topic = msg[topicStartPoint : topicEndPoint + 1].decode("utf-8")
    if lifecycle.authTokenMgrIns:
        lifecycle.authTokenMgrIns.updateTrustTokenFromTopic(topic)
    if controls["qos"] != 0:
        try:
            msgId = (msg[topicEndPoint + 1] << 8) + msg[topicEndPoint + 2]
        except IndexError:
            logger.error(f"topicEndPoint: {topicEndPoint}")
            logger.error(f"msg cause the issue: {msg}")
            msgId = None
    else:
        msgId = None
    nextTick = topicEndPoint + 3 if controls["qos"] != 0 else topicEndPoint + 1
    messageBytes = msg[nextTick:]
    decodedMsg = messageBytes.decode("utf-8")
    try:
        message = json.loads(decodedMsg)
        parsed = True
    except json.JSONDecodeError:
        logger.warning(f"⚠ Failed to resolve publish packet as JSON: {decodedMsg}")
        message = decodedMsg
        parsed = False
    return {
        "topic": topic,
        "id": msgId,
        "message": message,
        "parsed": parsed,
        "beginOfMessage": nextTick,
    }


def generateRemainLengthBytes(desiredRemainLength: int) -> bytes:
    result = b""
    value = desiredRemainLength

    while True:
        byte = value % 128
        value //= 128

        if value > 0:
            byte |= 128

        result += bytes([byte])

        if value == 0:
            break

    return result


def regeneratePacket(oldPacket: bytes, newPacketProperties: dict) -> bytes:
    packetType = oldPacket[0:1]

    originalPacketRemainLength = (
        len(oldPacket) - newPacketProperties["beginOfMutableHeader"]
    )
    mutableHeaderLength = (
        newPacketProperties["beginOfMessage"]
        - newPacketProperties["beginOfMutableHeader"]
    )
    originalPacketMessageLength = originalPacketRemainLength - mutableHeaderLength

    mutableHeader = oldPacket[
        newPacketProperties["beginOfMutableHeader"] : newPacketProperties[
            "beginOfMessage"
        ]
    ]

    encodedNewPacket = json.dumps(newPacketProperties["newPacketDict"]).encode("utf-8")
    packetMsgLengthDiff = len(encodedNewPacket) - originalPacketMessageLength
    newPacketRemainLength = originalPacketRemainLength + packetMsgLengthDiff

    newPacketRemainLengthBin = generateRemainLengthBytes(newPacketRemainLength)
    result = packetType + newPacketRemainLengthBin + mutableHeader + encodedNewPacket
    return result


def packetResolver(msg: TCPMessage):
    side = "Server 🔻" if msg.from_client != True else "Client 🔺"
    if (
        lifecycle.isDebug
    ):  # 如果不加这个判断, 非 Debug 模式下每个 Packet 会浪费一次获取 Timestamp 的性能
        logger.debug(
            f"MITM | TCP | {side} | OnTCPMessageRecv 📢 | TCP message detected, msgTs: {str(msg.timestamp).replace(".", "")}"
        )
    if isinstance(msg.content, bytes):
        pendingPackets = []
        pendingPackets = validatePackage(msg.content, pendingPackets, msg.from_client)
        if (
            lifecycle.isDebug
        ):  # 理论上来说, 非 Debug 模式下即使 logger.debug 不会输出, 但调用也会带来额外的性能开销
            logger.debug(
                f"MITM | TCP | {side} | OnTCPMsgSplitted ⛓️‍💥 | TCP packets are splitting into: \r\n{pendingPackets}"
            )
        resultArr = []
        for perPacket in pendingPackets:
            packetType = perPacket["type"]
            length = perPacket["length"]
            controls = None

            resolveResult = {}
            match packetType:
                case MQTT_PACKET_TYPES.PUBLISH.value:
                    controls = determineControls(perPacket["packet"])
                    resolveResult = resolvePublishPacket(
                        perPacket["packet"],
                        perPacket["beginOfMutableHeader"],
                        length,
                        controls,
                    )

                    rewriteResult = (
                        handlePublishPacket(
                            resolveResult["message"],
                            resolveResult["topic"],
                            msg.from_client,
                        )
                        if resolveResult["parsed"]
                        else resolveResult["message"]
                    )
                    resultArr.append(
                        {
                            "newPacketDict": rewriteResult["result"],
                            "originalPacket": perPacket["packet"],
                            "packetType": packetType,
                            "beginOfMutableHeader": perPacket["beginOfMutableHeader"],
                            "beginOfMessage": resolveResult["beginOfMessage"],
                            "noRewrite": rewriteResult["noRewrite"],
                        }
                    )

                case _:
                    resultArr.append(
                        {
                            "newPacketDict": perPacket["packet"],
                            "originalPacket": perPacket["packet"],
                            "packetType": packetType,
                            "beginOfMutableHeader": perPacket["beginOfMutableHeader"],
                            "beginOfMessage": None,
                            "noRewrite": True,
                        }
                    )

            if lifecycle.isDebug:
                logger.debug(
                    f"MITM | TCP | {side} | OnPackageProcessedSuc ✨ | New packet successfully processed.\r\n--- ✡️ Packet type ---\r\n[{packetType.upper()}]\r\n--- 🔢 Length info ---\r\n{length}\r\n--- ⚙️ Controls ---\r\n{controls}\r\n--- ✅ Resolve result (without rewrite) ---\r\n{resolveResult}"
                )

        finalPackets = []
        packetsEdited = False
        for packet in resultArr:
            finalPackets.append(
                regeneratePacket(packet["originalPacket"], packet)
                if not packet["noRewrite"]
                else packet["originalPacket"]
            )
            # Debug
            if not packet["noRewrite"] and not packetsEdited:
                packetsEdited = True

        if packetsEdited and lifecycle.isDebug:
            logger.debug(
                f"MITM | TCP | {side} | OnRewriteCompleted 👻 | Packets rewrite succeed. New TCP packets: {finalPackets}"
            )
        return finalPackets
    else:
        return [msg.content]
