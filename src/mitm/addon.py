from mitmproxy.tcp import TCPFlow
from mitmproxy.udp import UDPFlow
from mitmproxy.http import HTTPFlow
import sys
import asyncio

import lifecycle
from middleware.wsSender import broadcastWsMsg
from mitm.msgConstructor import constructHttpConnectionMsg, constructTcpConnectionMsg
from mitm.mqttPacketResolver import packetResolver


class MQTTAddonClass:
    def __init__(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        self.rules = {}
        self.logger = lifecycle.loggerInstance
        self.logger.success("👍 Successfully loaded mitmproxy addon")

    def tcp_message(self, flow: TCPFlow):
        resolveResultArr = packetResolver(flow.messages[-1])
        resolveResult = b""
        for result in resolveResultArr:
            resolveResult += result
        flow.messages[-1].content = resolveResult

    def request(self, flow: HTTPFlow):
        self.logger.debug("🔠 Detected HTTP request event:")
        self.logger.debug(flow)
