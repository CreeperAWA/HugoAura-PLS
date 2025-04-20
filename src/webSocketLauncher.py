import asyncio
from typing import Any
from websockets import ServerConnection, broadcast
from websockets.asyncio.server import serve
from loguru import logger

from middleware.auth import getAuthStatus


userConnections = set()
wsServerIns = None
authToken = ""


async def wsHandler(websocket: ServerConnection):
    global authToken
    global userConnections
    authResult = getAuthStatus(authToken, websocket)
    if authResult == False:
        await websocket.close()
        return
    userConnections.add(websocket)
    async for data in websocket:
        logger.debug(f"New WebSocket data received: {data}")

    logger.info(f"Client {websocket.id} disconnected, bye.")
    userConnections.remove(websocket)


async def broadcastMessage(message: Any):
    global wsServerIns
    if wsServerIns:
        broadcast(userConnections, message)


async def launchWebSocket(wsHost: str, wsPort: int, sslContext):
    global wsServerIns
    async with serve(
        wsHandler,
        host=wsHost,
        port=wsPort,
        server_header="AuraPLSWebSocket/1.0.0",
        ssl=sslContext,
    ) as wsServer:
        wsServerIns = wsServer
        logger.info(
            f"WebSocket server listening on ws{'' if sslContext == None else 's'}://{wsHost}:{wsPort}/"
        )
        await wsServer.serve_forever()


async def asyncLaunchWS(
    wsHost="127.0.0.1", wsPort=22077, authTokenArg="66CCFF", sslContext=None
):
    global authToken
    authToken = authTokenArg
    await launchWebSocket(wsHost, wsPort, sslContext)
