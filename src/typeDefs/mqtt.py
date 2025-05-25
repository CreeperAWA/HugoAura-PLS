from enum import Enum
from typing import TypedDict


class MQTT_PACKET_TYPES(Enum):
    CONNECT = "connect"
    CONNACK = "connack"
    PUBLISH = "publish"
    PUBACK = "puback"
    SUBSCRIBE = "subscribe"
    SUBACK = "suback"
    UNSUBSCRIBE = "unsubscribe"
    UNSUBACK = "unsuback"
    PINGREQ = "pingreq"
    PINGRESP = "pingresp"
    DISCONN = "disconnect"
    RESERVED = "reserved"
    UNKNOWN = "unknown"


class mqttResolverRet(TypedDict):
    type: MQTT_PACKET_TYPES
    topic: str
    length: int
    content: str | dict
