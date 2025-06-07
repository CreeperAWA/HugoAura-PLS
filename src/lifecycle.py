from argparse import Namespace
from pathlib import Path
from typing import Any

from utils.authTokenMgr import AuthTokenManager
from utils.registryMgr import RegistryManager


serviceMode = False
isDebug = False
cliArgv = Namespace()

wsServerInstance = None
loggerInstance: Any = None

authTokenMgrIns: AuthTokenManager | None = None
registryMgrIns: RegistryManager | None = None

userConnections = set()
devUserConnections = set()

appConfig: Any = {}
plsDataDir = Path()
meiPassDir = None

ruleMapping = {}
