from loguru import logger
from websockets import ServerConnection

import services.config as configSrv
from routes.error import constructRouteNotFound

from typeDefs.websocketRoutes.config import UPDATE_CONFIG_RETURN
from typeDefs.websocket import wsBaseRet


def configRouteHandler(
    subLevelRoute: str, client: ServerConnection, clientData: dict
) -> wsBaseRet:
    match subLevelRoute:
        case "getBasicConfig":
            data = configSrv.getBasicConfig()
            return {
                "success": True if data != None else False,
                "code": 0 if data != None else 2001,
                "data": (
                    data if data != None else {"message": "Config not initialized."}
                ),
            }

        case "getRuleSettings":
            data = configSrv.getRuleSettings()
            return {
                "success": True if data != None else False,
                "code": 0 if data != None else 2011,
                "data": (
                    data
                    if data != None
                    else {"message": "Rule Settings not initialized."}
                ),
            }

        case "updateConfig":
            try:
                result = configSrv.updateConfig(
                    clientData["key"], clientData["value"]
                )
            except Exception as err:
                result = UPDATE_CONFIG_RETURN.UNEXPECTED_ERROR
                logger.error(f"An error occurred updating config:")
                logger.error(err)
            match result:
                case UPDATE_CONFIG_RETURN.KEY_NOT_FOUND:
                    return {
                        "success": False,
                        "code": 2021,
                        "data": {"message": "Target key not found."},
                    }
                case UPDATE_CONFIG_RETURN.UNEXPECTED_ERROR:
                    return {
                        "success": False,
                        "code": 2022,
                        "data": {"message": "Unexpected error occurred."},
                    }
                case UPDATE_CONFIG_RETURN.SUCCESS:
                    return {
                        "success": True,
                        "code": 0,
                        "data": {"message": "Successfully updated config."},
                    }

        case _:
            return constructRouteNotFound()
