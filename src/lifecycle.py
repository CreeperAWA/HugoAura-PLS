from argparse import Namespace
from typing import Any


isDebug = False
cliArgv = Namespace()

wsServerInstance = None
loggerInstance: Any = None

userConnections = set()
devUserConnections = set()

appConfig: Any = {}
plsDataDir = ""
meiPassDir = None

ruleMapping = {}
