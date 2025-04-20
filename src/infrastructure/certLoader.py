import ssl
from loguru import logger


def createSSLContext(userConfig, type):
    try:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        if type == "ws":
            ssl_context.load_cert_chain(userConfig.certPath, keyfile=userConfig.keyPath)
            return ssl_context
        elif type == "mqtt":
            ssl_context.load_cert_chain(
                userConfig.mqttCertPath, keyfile=userConfig.mqttKeyPath
            )
            return ssl_context
        else:
            logger.error(f"Unknown TLS certs type: {type}")
            return None
    except Exception as e:
        logger.error(f"Error reading TLS certs: {e}")
        return None
