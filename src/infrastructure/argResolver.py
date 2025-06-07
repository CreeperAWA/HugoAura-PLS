import argparse


def parseArgv(bypass=False):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cli",
        required=False,
        help="Run as CLI",
    )
    parser.add_argument("--debug", required=False, help="Enable debugging features")
    result = None
    if not bypass:
        result = parser.parse_args()
    else:
        result = parser.parse_args([])
    return result
