import json
import asyncio
from typing import Any
from websockets import ServerConnection, broadcast
from websockets.asyncio.server import serve
from loguru import logger

import lifecycle
from middleware.auth import getAuthStatus
from routes.router import router
from services.basic import initialPush


wsServerIns = None
authToken = ""


async def wsHandler(websocket: ServerConnection):
    global authToken
    authResult = getAuthStatus(authToken, websocket)
    if not authResult:
        await websocket.close()
        return
    lifecycle.userConnections.add(websocket)
    await initialPush(websocket)
    async for data in websocket:
        logger.debug(f"⏬ New WebSocket data received: {data}")
        try:
            parsedData = json.loads(data)
        except:
            logger.error(f"Error parsing client data: {data}")
            parsedData = {}
        asyncio.create_task(router(websocket, parsedData)) # type: ignore

    logger.info(f"Client {websocket.id} disconnected, bye.")
    lifecycle.userConnections.remove(websocket)


async def broadcastMessage(message: Any):
    global wsServerIns
    if wsServerIns:
        broadcast(lifecycle.userConnections, message)


async def launchWebSocket(wsHost: str, wsPort: int, sslContext):
    global wsServerIns
    if sslContext != None and lifecycle.cliArgv.ws_insecure == "true":
        async with serve(
            wsHandler,
            host=wsHost,
            port=wsPort,
            server_header="AuraPLSWebSocket/1.0.0",
        ) as wsNonSSLServer:
            lifecycle.wsServerInstance = wsNonSSLServer
            wsServerIns = wsNonSSLServer
            logger.success(f"🎉 WebSocket debug server listening on ws://{wsHost}:{wsPort}/")
            await wsNonSSLServer.serve_forever()
    else:
        async with serve(
            wsHandler,
            host=wsHost,
            port=wsPort,
            server_header="AuraPLSWebSocket/1.0.0",
            ssl=sslContext,
        ) as wsServer:
            lifecycle.wsServerInstance = wsServer
            wsServerIns = wsServer
            logger.success(
                f"🎉 WebSocket server listening on ws{'' if sslContext == None else 's'}://{wsHost}:{wsPort}/"
            )
            await wsServer.serve_forever()


async def asyncLaunchWS(
    wsHost="127.0.0.1", wsPort=22077, authTokenArg="66CCFF", sslContext=None
):
    global authToken
    authToken = authTokenArg
    await launchWebSocket(wsHost, wsPort, sslContext)
