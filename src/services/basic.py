from __init__ import __VERSION__

from middleware.wsSender import sendWsMsg
from services.config import pushConfig
from lifecycle import devUserConnections

from typeDefs.websocket import wsBasePush
from websockets import ServerConnection
from typeDefs.websocketRoutes.basic import PLS_STATUS, PLSInfo


def getPlsInfo() -> PLSInfo:
    return PLSInfo(status=PLS_STATUS.RUNNING, version=__VERSION__)


def pushPlsInfo() -> wsBasePush:
    data = {}
    try:
        data = getPlsInfo()
        success = True
    except:
        data = {}
        success = False
    return {"success": success, "data": data, "type": "basic.action.pushPlsInfo"}


def setClientType(ws: ServerConnection, isDev: bool):
    try:
        if isDev:
            devUserConnections.add(ws)
        else:
            try:
                devUserConnections.remove(ws)
            except KeyError:
                pass
        success = True
    except:
        success = False
    return success


async def initialPush(ws: ServerConnection):
    await sendWsMsg(ws, data=pushPlsInfo())
    await sendWsMsg(ws, data=pushConfig("basic"))
    await sendWsMsg(ws, data=pushConfig("rule"))

    await sendWsMsg(
        ws,
        data={
            "success": True,
            "data": {"message": "Push completed."},
            "type": "basic.event.initialPushSuccess",
        },
    )
