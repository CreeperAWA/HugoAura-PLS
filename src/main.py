import sys
import os

srcDir = os.path.dirname(os.path.abspath(__file__))
if srcDir not in sys.path:
    sys.path.insert(0, srcDir)

import asyncio
from pathlib import Path
from loguru import logger

import lifecycle
from config.manager import loadConfig
from infrastructure.argResolver import parseArgv
from infrastructure.logger import setupLogger
from infrastructure.certLoader import createSSLContext
from mitm.manager import startProxy
from webSocketLauncher import asyncLaunchWS
from mitm.ruleLoader import loadRules


async def main():
    plsDataDir = Path.joinpath(Path.home(), "Documents", "HugoAura", "Aura-PLS")
    lifecycle.plsDataDir = plsDataDir

    cliArgv = parseArgv()
    lifecycle.cliArgv = cliArgv
    lifecycle.isDebug = cliArgv.debug == "true"

    setupLogger(lifecycle.isDebug)
    logger.info("🚀 Logger initialized.")

    logger.debug(f"⌨️ CLI args: {cliArgv}")

    if hasattr(sys, "_MEIPASS"):
        logger.debug(f"Running in packaged mode, _MEIPASS: {sys._MEIPASS}")  # type: ignore
        lifecycle.meiPassDir = sys._MEIPASS  # type: ignore

    config = loadConfig(str(Path.joinpath(plsDataDir, "config", "user.json")))
    logger.success("📋 Successfully loaded config.")
    logger.debug(f"📜 User config: {config}")

    logger.info("🔒 Creating SSL Context for WebSocket server...")
    wsSSLContext = createSSLContext(config, "ws")

    logger.info("⌛ Starting WebSocket server...")
    asyncio.create_task(
        asyncLaunchWS(
            config.wsHost, config.wsPort, cliArgv.aura_pls_auth_token, wsSSLContext
        )
    )

    logger.info("🍭 Starting rules loader...")
    loadRules()

    logger.info("🔍 Starting MitmProxy...")
    asyncio.create_task(startProxy())
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.error("👋 Exiting Aura-PLS...")
        exit(0)
