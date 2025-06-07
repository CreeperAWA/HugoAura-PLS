from enum import Enum
from typing import Any, NotRequired, TypedDict


type _KeyType = Any # The _KeyType in winreg is private

class SharedErrors(Enum):
    UNKNOWN_ERROR = "UnknownError"
    FAILED_TO_WRITE = "FailedToWrite"


class OpenKeyErrors(Enum):
    KEY_NOT_FOUND = "KeyNotFound"


class OpenKeyRet(TypedDict):
    success: bool
    data: _KeyType | None
    error: OpenKeyErrors | None
    errorObj: NotRequired[OSError | None]


class QueryValRetData(TypedDict):
    value: Any
    type: int


class QueryValErrors(Enum):
    KEY_NOT_FOUND = "KeyNotFound"
    VAL_NOT_FOUND = "ValueNotFound"


class QueryValRet(TypedDict):
    success: bool
    data: QueryValRetData | None
    error: QueryValErrors | None
    errorObj: NotRequired[OSError | None]


class InitRegRet(TypedDict):
    success: bool
    data: _KeyType | None
    error: SharedErrors | None
    errorObj: NotRequired[Exception | None]


class UpdateValRet(TypedDict):
    success: bool
    error: SharedErrors | OpenKeyErrors | None
    errorObj: NotRequired[OSError | None]


class DeleteValRet(TypedDict):
    success: bool
    error: SharedErrors | OpenKeyErrors | None
    errorObj: NotRequired[OSError | None]


class DeleteKeyRet(TypedDict):
    success: bool
    error: SharedErrors | OpenKeyErrors | None
    errorObj: NotRequired[OSError | Exception | None]
