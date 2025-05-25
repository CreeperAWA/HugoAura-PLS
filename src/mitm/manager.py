from loguru import logger
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster

from mitm.addon import MQTTAddonClass


async def startProxy(procName: str = "SeewoCore.exe"):
    mitmproxyLaunchOptions = Options(mode=[f"local:{procName}"], ssl_insecure=True)

    master = DumpMaster(mitmproxyLaunchOptions, with_dumper=False)
    master.addons.add(MQTTAddonClass())
    
    await master.run()
