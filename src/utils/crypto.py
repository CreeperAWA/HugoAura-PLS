import random
import secrets


def genRandomHex(length=16, secure=False):
    result = None
    if secure:
        result = secrets.token_hex(length // 2).zfill(length)
    else:
        result = "".join(random.choice("0123456789abcdef") for _ in range(length))
    return result
