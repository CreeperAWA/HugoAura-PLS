from loguru import logger
from websockets import ServerConnection

from middleware.wsSender import sendWsWithEvtId

from routes.basic import basicRouteHandler
from routes.error import constructRouteNotFound
from routes.config import configRouteHandler

from typeDefs.websocket import wsBaseReq, wsBaseRet


async def router(client: ServerConnection, clientFullData: wsBaseReq):
    # Example: basic.action.getPlsInfo
    method = clientFullData["method"]
    eventId = clientFullData["eventId"]

    operationCategory = method.split(".")[0]
    operationVerb = method.split(".")[1]
    operationTarget = method.split(".")[2]
    try:
        match operationCategory:
            case "basic":
                result = basicRouteHandler(
                    operationTarget, client, clientFullData["data"]
                )
            case "config":
                result = configRouteHandler(
                    operationTarget, client, clientFullData["data"]
                )
            case _:
                result = constructRouteNotFound()
    except Exception as err:
        result: wsBaseRet = {
            "success": False,
            "code": -1,
            "data": {"message": "Unexpected error occurred."},
        }
        logger.error(f"Exception occurred processing ws msg:\r\n{err}")

    return await sendWsWithEvtId(client, eventId, result)
