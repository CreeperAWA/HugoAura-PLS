import asyncio
from pathlib import Path
import sys

import lifecycle
from loguru import logger
from config.manager import loadConfig
from infrastructure.certLoader import createSSLContext, generateSelfSignedCert
from mitm.manager import startProxy
from webSocketLauncher import asyncLaunchWS
from mitm.ruleLoader import loadRules
from utils.authTokenMgr import AuthTokenManager
from utils.registryMgr import RegistryManager


async def main(stopEvent: asyncio.Event | None = None):
    plsDataDir = lifecycle.plsDataDir
    if hasattr(sys, "_MEIPASS"):
        logger.debug(f"Running in packaged mode, _MEIPASS: {sys._MEIPASS}")  # type: ignore
        lifecycle.meiPassDir = sys._MEIPASS  # type: ignore

    config = loadConfig(str(Path.joinpath(plsDataDir, "config", "user.json")))
    logger.success("📋 Successfully loaded config.")
    logger.debug(f"📜 User config: {config}")

    logger.info("✒️ Initializing Registry Manager...")
    lifecycle.registryMgrIns = RegistryManager()
    lifecycle.registryMgrIns.initRegistryKey(autoClose=True)

    logger.info("🗝️ Initializing Auth Token Manager...")
    lifecycle.authTokenMgrIns = AuthTokenManager()
    lifecycle.authTokenMgrIns.generateAndWriteAuthToken()

    logger.info("🛡️ Initializing TLS certificate...")
    if config.regenCert:
        result = generateSelfSignedCert(config)
        if not result:
            logger.error("⛔ TLS certificate initialization failed, exiting PLS...")
            exit(-2)
    else:
        certFullPathExists = Path.joinpath(
            Path(plsDataDir), Path(config.certPath)
        ).exists()
        keyFullPathExists = Path.joinpath(
            Path(plsDataDir), Path(config.keyPath)
        ).exists()
        if not certFullPathExists or not keyFullPathExists:
            logger.error(
                f"⛔ TLS {"certificate" if not certFullPathExists else "key"} path invalid, exiting PLS..."
            )
            exit(-3)

    logger.info("🔒 Creating SSL Context for WebSocket server...")
    wsSSLContext = createSSLContext(config, "ws")

    logger.info("⌛ Starting WebSocket server...")
    asyncio.create_task(asyncLaunchWS(config.wsHost, config.wsPort, wsSSLContext))

    logger.info("🍭 Starting rules loader...")
    loadRules()

    logger.info("🔍 Starting MitmProxy...")
    asyncio.create_task(startProxy()) # type: ignore

    if stopEvent:
        logger.success("✅ Service started successfully. Waiting for stop signal...")
        await stopEvent.wait()
        logger.info("🛑 Stop signal received, shutting down all tasks...")
    else:
        logger.success("✅ Application started in CLI mode. Press Ctrl+C to exit.")
        await asyncio.Event().wait()
