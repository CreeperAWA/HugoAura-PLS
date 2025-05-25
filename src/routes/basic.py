from loguru import logger
from lifecycle import devUserConnections
from services.basic import getPlsInfo, setClientType

from routes.error import constructRouteNotFound
from typeDefs.websocket import wsBaseRet
from websockets import ServerConnection


def basicRouteHandler(
    subLevelRoute: str, client: ServerConnection, clientData: dict
) -> wsBaseRet:
    match subLevelRoute:
        case "getPlsInfo":
            data = {}
            try:
                data = getPlsInfo()
                success = True
            except:
                success = False
            return {
                "success": success,
                "code": 0 if success else 1001,
                "data": data,
            }
        case "setClientType":
            data = {}
            result = setClientType(
                client, True if clientData["type"] == "dev" else False
            )
            logger.debug(devUserConnections)
            return {
                "success": result,
                "code": 0 if result else 1011,
                "data": {"message": "Success" if result else "Failed"},
            }
        case _:
            return constructRouteNotFound()
