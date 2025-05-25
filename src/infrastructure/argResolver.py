import argparse


def parseArgv():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--aura-pls-auth-token",
        required=True,
        help="Aura ProxyLayerServices WebSocket server authorization token",
    )
    parser.add_argument(
        "--ws-port",
        required=False,
        help="Aura ProxyLayerServices WebSocket server port",
    )
    parser.add_argument("--debug", required=False, help="Enable debugging features")
    parser.add_argument(
        "--ws-insecure", required=False, help="Disable wss for WebSocket server"
    )
    result = parser.parse_args()
    return result
