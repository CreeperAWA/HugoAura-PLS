import sys
import os


srcDir = os.path.dirname(os.path.abspath(__file__))
if srcDir not in sys.path:
    sys.path.insert(0, srcDir)

import asyncio
import win32serviceutil
from pathlib import Path
from loguru import logger

import lifecycle
from infrastructure.winSvc import AuraPLSService
from infrastructure.argResolver import parseArgv
from infrastructure.logger import setupLogger
from appLauncher import main

if __name__ == "__main__":
    plsDataDir = Path.joinpath(Path.home(), "Documents", "HugoAura", "Aura-PLS")
    lifecycle.plsDataDir = plsDataDir

    cliArgv = parseArgv()
    lifecycle.serviceMode = True if cliArgv.service else False
    lifecycle.cliArgv = cliArgv
    lifecycle.isDebug = cliArgv.debug == "true"

    setupLogger(lifecycle.isDebug, lifecycle.serviceMode, plsDataDir)
    logger.info("🚀 Logger initialized.")

    logger.debug(f"⌨️ CLI args: {cliArgv}")

    if lifecycle.serviceMode:
        win32serviceutil.HandleCommandLine(
            AuraPLSService, argv=[sys.argv[0], cliArgv.service]
        )
    else:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            logger.error("👋 Exiting Aura-PLS...")
            exit(0)
