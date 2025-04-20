import asyncio
from loguru import logger

from config.loader import loadConfig
from infrastructure.argResolver import parseArgv
from infrastructure.logger import setupLogger
from infrastructure.certLoader import createSSLContext
from webSocketLauncher import asyncLaunchWS


async def main():
    setupLogger()
    logger.info("Logger initialized.")

    config = loadConfig()
    logger.info("Successfully loaded config.")
    logger.debug(f"User config: {config}")

    cliArgv = parseArgv()
    logger.debug(f"CLI args: {cliArgv}")

    logger.info("Creating SSL Context for WebSocket server...")
    wsSSLContext = createSSLContext(config, "ws")

    logger.info("Starting WebSocket server...")
    asyncio.create_task(
        asyncLaunchWS(
            config.wsHost, config.wsPort, cliArgv.aura_pls_auth_token, wsSSLContext
        )
    )

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
