from pathlib import Path
import ssl
from loguru import logger

import lifecycle


def createSSLContext(userConfig, type):
    try:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        if type == "ws":
            ssl_context.load_cert_chain(
                Path.joinpath(Path(lifecycle.plsDataDir), Path(userConfig.certPath)),
                keyfile=Path.joinpath(
                    Path(lifecycle.plsDataDir), Path(userConfig.keyPath)
                ),
            )
            return ssl_context
        else:
            logger.error(f"Unknown TLS certs type: {type}")
            return None
    except Exception as e:
        logger.error(f"Error reading TLS certs: {e}")
        return None
