import hashlib
from loguru import logger

import lifecycle
from utils.crypto import genRandomHex


class AuthTokenManager:
    def __init__(self):
        self.curAuthToken = ""
        # self.finalAuthSHA512 = "" // no, for safety

    def getSHA512Val(self, authToken=None) -> str:
        if not authToken:
            authToken = self.curAuthToken
        conjVal = authToken + "AuraXAuth 0xFFFFFF NeverEnds"
        conjValBytes = conjVal.encode("utf-8")
        cryptoIns = hashlib.sha512()
        cryptoIns.update(conjValBytes)

        return cryptoIns.hexdigest()

    def generateAndWriteAuthToken(self):
        if not lifecycle.registryMgrIns:
            return {"success": False, "data": None}

        self.curAuthToken = genRandomHex(32, True)
        result = lifecycle.registryMgrIns.createOrUpdateRegistryValue(
            lifecycle.registryMgrIns.rootClass,
            lifecycle.registryMgrIns.path,
            "AuthToken",
            self.curAuthToken,
        )
        return {
            "success": result["success"],
            "data": self.curAuthToken if result["success"] else None,
            "error": result["error"],
        }
