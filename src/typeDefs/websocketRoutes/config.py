from enum import Enum
from typing import TypedDict


class AuraPLSBaseConfig(TypedDict):
    proxyProcArr: list[str]
    wsHost: str
    wsPort: int
    certPath: str
    keyPath: str


class UPDATE_CONFIG_RETURN(Enum):
    KEY_NOT_FOUND = "keyNotFound"
    UNEXPECTED_ERROR = "unexpectedError"
    SUCCESS = "success"
