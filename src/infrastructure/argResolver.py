import argparse


def parseArgv():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ws-port",
        required=False,
        help="Aura ProxyLayerServices WebSocket server port",
    )
    parser.add_argument("--debug", required=False, help="Enable debugging features")
    parser.add_argument(
        "--ws-insecure", required=False, help="Disable wss for WebSocket server"
    )
    parser.add_argument("--service", required=False, help="Launch as service mode")
    result = parser.parse_args()
    return result
