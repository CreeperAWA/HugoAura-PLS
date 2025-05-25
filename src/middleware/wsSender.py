import asyncio
from enum import Enum
import json

from loguru import logger
from websockets import ServerConnection
from lifecycle import userConnections, devUserConnections

from typeDefs.websocket import wsBasePush, wsBaseRet, wsFinRet


class EnumJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Enum):
            return o.value
        return super().default(o)


async def sendWsWithEvtId(ws: ServerConnection, eventId: str, data: wsBaseRet):
    dataWithEvtId: wsFinRet = {**data, "eventId": eventId}
    result = await sendWsMsg(ws, dataWithEvtId)
    return result


async def sendWsMsg(ws: ServerConnection, data: wsFinRet | wsBasePush):
    logger.debug(f"Sending ws message to client {ws.id}: {data}")
    result = await ws.send(json.dumps(data, cls=EnumJSONEncoder))
    return result


async def broadcastWsMsg(data: wsFinRet | wsBasePush, devOnly=False):
    # logger.debug(f"Broadcasting message: {data}")
    for connection in userConnections if not devOnly else devUserConnections:
        asyncio.create_task(connection.send(json.dumps(data, cls=EnumJSONEncoder)))
