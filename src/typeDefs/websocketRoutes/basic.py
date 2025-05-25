from enum import Enum
from typing import TypedDict


class PLS_STATUS(Enum):
    RUNNING = "running"
    WARNING = "warning"
    CRITICAL = "critical"


class PLSInfo(TypedDict):
    status: PLS_STATUS
    version: str
