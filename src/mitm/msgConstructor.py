from mitmproxy.tcp import TCPFlow
from mitmproxy.udp import UDPFlow
from mitmproxy.http import HTTPFlow

from typeDefs.websocket import wsBasePush


def constructTcpConnectionMsg(flow: TCPFlow):
    primi = {"lastMsg": flow.messages[-1].content}
    return finWrapper(primi, "TCP", flow)


def constructHttpConnectionMsg(flow: HTTPFlow):
    primi = {"request": flow.request.content, "response": flow.response.content if flow.response != None else ""}
    return finWrapper(primi, "HTTP", flow)


def constructUdpConnectionMsg(flow: UDPFlow):
    primi = {"lastMsg": flow.messages[-1].content}
    return finWrapper(primi, "UDP", flow)


def finWrapper(primitive: dict, method: str, flow: TCPFlow | UDPFlow | HTTPFlow) -> wsBasePush:
    return {
        "success": True,
        "data": {
            **primitive,
            "client": f"{flow.client_conn.address[0]}:{flow.client_conn.address[1]}",
            "server": (
                f"{flow.server_conn.address[0]}:{flow.server_conn.address[1]}"
                if flow.server_conn.address != None
                else ""
            ),
        },
        "type": f"proxy.connect.intercepted{method}Connection",
    }
