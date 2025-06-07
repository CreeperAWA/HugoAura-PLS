import hashlib
from loguru import logger

import lifecycle
from utils.crypto import genRandomHex


class AuthTokenManager:
    def __init__(self):
        self.curAuthToken = ""
        self.trustToken = ""
        # self.finalAuthSHA512 = "" // no, for safety

    def getSHA512Val(self, authToken=None, trustToken=None) -> str:
        if not authToken:
            authToken = self.curAuthToken
        if not trustToken:
            trustToken = self.trustToken
        conjVal = authToken + "AuraXAuth" + trustToken + "NeverEnds"
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

    def updateTrustToken(self, token: str):
        self.trustToken = token

    def updateTrustTokenFromTopic(self, decodedTopic: str):
        if self.trustToken != "" and self.trustToken:
            return
        topicPathArr = decodedTopic.split("/")
        deviceId = topicPathArr[3]
        # logger.debug("Trust token updated: " + deviceId)
        logger.debug("🪙 Trust token updated: ******")
        self.updateTrustToken(deviceId)
