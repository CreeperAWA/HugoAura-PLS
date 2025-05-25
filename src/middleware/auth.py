from loguru import logger
from websockets import ServerConnection


def getAuthStatus(authToken: str, clientRequest: ServerConnection):
    if clientRequest.request == None:
        return False
    logger.debug(clientRequest.request.path)
    authHeader = clientRequest.request.headers.get("Authorization")
    if authHeader == None:
        # 一开始以为希沃管家的主进程会有 `ws` 模块, 没想到没有... 所以现在有两种认证模式
        # Authorization 的还是留着吧, 万一以后哪天要用...
        clientRequestAuthParams = clientRequest.request.path.split("auth=")
        if len(clientRequestAuthParams) > 1 and clientRequestAuthParams[1] == authToken:
            logger.info(
                f"Client {clientRequest.id} trying to connect with auth params {clientRequestAuthParams}, accepted."
            )
            return True
        return False
    if len(authHeader.split("Bearer ")) < 2:
        return False
    if authHeader.split("Bearer ")[1] != authToken:
        logger.warning(
            f"Client {clientRequest.id} trying to connect with invalid auth header {authHeader}, closing connection."
        )
        return False

    logger.info(
        f"Client {clientRequest.id} trying to connect with auth header {authHeader}, accepted."
    )
    return True
