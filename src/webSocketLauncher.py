import errno
import json
import asyncio
import random
from typing import Any
from websockets import ServerConnection, broadcast
from websockets.asyncio.server import serve
from loguru import logger

import lifecycle
from middleware.auth import getAuthStatus
from routes.router import router
from services.basic import initialPush


wsServerIns = None


async def wsHandler(websocket: ServerConnection):
    if not lifecycle.authTokenMgrIns:
        await websocket.close()
        return
    if (
        not lifecycle.authTokenMgrIns.trustToken
        or lifecycle.authTokenMgrIns.trustToken == ""
    ):
        await websocket.send(
            json.dumps(
                {
                    "success": False,
                    "type": "basic.plsNotReadyError",
                    "data": {"message": "PLS isn't ready."},
                }
            )
        )
        await websocket.close()
        return
    authResult = getAuthStatus(lifecycle.authTokenMgrIns.getSHA512Val(), websocket)
    if not authResult:
        await websocket.send(
            json.dumps(
                {
                    "success": False,
                    "type": "basic.authFailed",
                    "data": {"message": "Permission denied"},
                }
            )
        )
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
        asyncio.create_task(router(websocket, parsedData))  # type: ignore

    logger.info(f"Client {websocket.id} disconnected, bye.")
    lifecycle.userConnections.remove(websocket)


async def broadcastMessage(message: Any):
    global wsServerIns
    if wsServerIns:
        broadcast(lifecycle.userConnections, message)


def addWsPortRegKey(port: int, isSSL: bool):
    if lifecycle.registryMgrIns:
        root = lifecycle.registryMgrIns.rootClass
        path = lifecycle.registryMgrIns.path
        lifecycle.registryMgrIns.createOrUpdateRegistryValue(
            root,
            path,
            "WsPort",
            str(port),
        )
        lifecycle.registryMgrIns.createOrUpdateRegistryValue(
            root,
            path,
            "Protocol",
            "wss" if isSSL else "ws",
        )


async def launchWebSocket(wsHost: str, wsPort: int, sslContext):
    global wsServerIns

    useSSL = sslContext is not None and lifecycle.cliArgv.ws_insecure != "true"

    currentPort = wsPort
    maxRetries = 10

    for attempt in range(maxRetries):
        try:
            serveKwargs = {
                "handler": wsHandler,
                "host": wsHost,
                "port": currentPort,
                "server_header": "AuraPLSWebSocket/1.0.0",
            }

            if useSSL:
                serveKwargs["ssl"] = sslContext

            async with serve(**serveKwargs) as wsServer:
                lifecycle.wsServerInstance = wsServer
                wsServerIns = wsServer
                addWsPortRegKey(currentPort, useSSL)

                protocol = "wss" if useSSL else "ws"
                logger.success(
                    f"🎉 WebSocket {'debug ' if not useSSL else ''}server listening on {protocol}://{wsHost}:{currentPort}/"
                )

                await wsServer.serve_forever()

        except OSError as e:
            if e.errno == errno.EADDRINUSE or e.errno == errno.EADDRNOTAVAIL:
                if attempt < maxRetries - 1:
                    logger.warning(
                        f"⚠ Port {currentPort} has been used, trying another one... ({attempt + 1}/{maxRetries})"
                    )
                    currentPort = random.randint(10000, 65535)
                else:
                    logger.error(
                        f"❌ Failed to find available port after {maxRetries} attempts"
                    )
                    raise
            else:
                logger.error(
                    f"❌ Unknown error occurred while launching ws server:\n{e}"
                )
                raise


async def asyncLaunchWS(wsHost="127.0.0.1", wsPort=22077, sslContext=None):
    await launchWebSocket(wsHost, wsPort, sslContext)
