import json
from loguru import logger
from pydantic import BaseModel
import shutil


class AuraPLSConfig(BaseModel):
    proxyProcArr: list[str]
    wsHost: str
    wsPort: int
    certPath: str
    keyPath: str
    mqttCertPath: str
    mqttKeyPath: str


def loadConfig(
    configPath="config/user.json", defaultConfPath="config/default.json"
) -> AuraPLSConfig:
    try:
        with open(configPath) as f:
            return AuraPLSConfig(**json.load(f))
    except FileNotFoundError:
        logger.warning(
            "No user config file found, creating a new config using config/default.json ..."
        )
        shutil.copyfile(defaultConfPath, configPath)
        with open(defaultConfPath) as f:
            return AuraPLSConfig(**json.load(f))
