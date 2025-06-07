import sys
import os


srcDir = os.path.dirname(os.path.abspath(__file__))
if srcDir not in sys.path:
    sys.path.insert(0, srcDir)

import asyncio
import win32serviceutil
import servicemanager
from pathlib import Path
from loguru import logger

import lifecycle
from infrastructure.winSvc import AuraPLSService, checkIsSvcCmd
from infrastructure.argResolver import parseArgv
from infrastructure.logger import setupLogger
from appLauncher import main

if __name__ == "__main__":
    if checkIsSvcCmd(sys.argv):
        lifecycle.serviceMode = True

    if lifecycle.serviceMode:
        programDataDir = os.getenv("PROGRAMDATA")
        plsDataDir = Path.joinpath(
            Path(programDataDir if programDataDir else "C:\\ProgramData"),
            "HugoAura",
            "PLS",
        )
    else:
        plsDataDir = Path.joinpath(Path.home(), "Documents", "HugoAura", "Aura-PLS")

    lifecycle.plsDataDir = plsDataDir

    if lifecycle.serviceMode:
        lifecycle.isDebug = False
        setupLogger(False, True)
        logger.info("Starting as serviceMode...")
        logger.info(f"Command line argv: {sys.argv}")

        if len(sys.argv) == 1:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(AuraPLSService)
            servicemanager.StartServiceCtrlDispatcher()
        else:
            win32serviceutil.HandleCommandLine(
                AuraPLSService,
            )
    else:
        cliArgv = parseArgv()
        lifecycle.cliArgv = cliArgv
        lifecycle.isDebug = cliArgv.debug == "true"

        setupLogger(lifecycle.isDebug, lifecycle.serviceMode)
        logger.info("🚀 Logger initialized.")

        logger.debug(f"⌨️ CLI args: {lifecycle.cliArgv}")

        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            logger.error("👋 Exiting Aura-PLS...")
            sys.exit(0)
