from loguru import logger
from mitmproxy import ctx
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster

from mitm.addon import MQTTAddonClass


async def startProxy(procName: str = "SeewoCore.exe"):
    mitmproxyLaunchOptions = Options()

    mitmproxyLaunchOptions.update(
        mode=[f"local:{procName}"],
        ssl_insecure=True,
        client_certs="config/mtls/Seewo_Core_Hardcoded_mTLS_Cert.pem",
    )

    master = DumpMaster(mitmproxyLaunchOptions, with_dumper=False)
    master.addons.add(MQTTAddonClass())
    ctx.options.tls_version_server_min = "TLS1"
    ctx.options.tls_version_client_min = "TLS1"
    # ↑ 为了兼容希沃安卓 MQTT mTLS 证书的上古 SHA1 算法

    await master.run()
