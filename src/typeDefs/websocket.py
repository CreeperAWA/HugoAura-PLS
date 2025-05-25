from typing import Any, TypedDict


class wsBaseReq(TypedDict):
    eventId: str
    method: str
    data: dict[Any, Any]


class wsBaseRet(TypedDict):
    success: bool
    code: int
    data: Any

class wsFinRet(wsBaseRet):
    eventId: str

class wsBasePush(TypedDict):
    success: bool
    data: Any
    type: str
