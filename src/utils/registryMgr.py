import winreg

from typeDefs.utils.registryMgr import (
    DeleteKeyRet,
    DeleteValRet,
    OpenKeyRet,
    OpenKeyErrors,
    QueryValErrors,
    QueryValRet,
    SharedErrors,
    UpdateValRet,
)


class RegistryManager:
    def __init__(
        self,
        rootClass=winreg.HKEY_CURRENT_USER, ## eqeqeq HKEY_USERS/.DEFAULT in serviceMode
        path=["SOFTWARE", "HugoAura", "ProxyLayerServices"],
    ):
        self.rootClass = rootClass
        self.path = path

    def openKey(self, root, path) -> OpenKeyRet:
        try:
            key = winreg.OpenKey(root, "\\".join(path), 0, winreg.KEY_ALL_ACCESS)
            return {"success": True, "data": key, "error": None}
        except OSError as err:
            return {
                "success": False,
                "data": None,
                "error": OpenKeyErrors.KEY_NOT_FOUND,
                "errorObj": err,
            }

    def queryValue(self, root, path, valName) -> QueryValRet:
        try:
            targetKey = self.openKey(root, "\\".join(path))
            if not targetKey["success"] or not targetKey["data"]:
                return {
                    "success": False,
                    "data": None,
                    "error": QueryValErrors.KEY_NOT_FOUND,
                }

            value, type = winreg.QueryValueEx(targetKey["data"], valName)

            winreg.CloseKey(targetKey["data"])
            return {
                "success": True,
                "data": {"value": value, "type": type},
                "error": None,
            }
        except OSError as err:
            return {
                "success": False,
                "data": None,
                "error": QueryValErrors.VAL_NOT_FOUND,
                "errorObj": err,
            }

    def getOrCreateRegKeyRecursive(self, root, path):
        curKey = root
        for subKey in path:
            try:
                key = winreg.OpenKey(curKey, subKey, 0, winreg.KEY_ALL_ACCESS)
            except OSError:
                key = winreg.CreateKey(curKey, subKey)
            winreg.CloseKey(key)
            curKey = winreg.OpenKey(curKey, subKey, 0, winreg.KEY_ALL_ACCESS)
        return curKey

    def initRegistryKey(self, root=None, path=None, autoClose=True):
        if not root:
            root = self.rootClass
        if not path:
            path = self.path

        try:
            plsKey = self.getOrCreateRegKeyRecursive(root, path)
            if autoClose:
                winreg.CloseKey(plsKey)
            return {
                "success": True,
                "data": plsKey if not autoClose else None,
                "error": None,
            }
        except Exception as err:
            return {
                "success": False,
                "data": None,
                "error": SharedErrors.UNKNOWN_ERROR,
                "errorObj": err,
            }

    def createOrUpdateRegistryValue(self, root, path, valName, valData) -> UpdateValRet:
        openKeyRet = self.openKey(root, path)
        if not openKeyRet["success"] or not openKeyRet["data"]:
            return {"success": False, "error": openKeyRet["error"]}
        targetKey = openKeyRet["data"]
        try:
            winreg.SetValueEx(targetKey, valName, 0, winreg.REG_SZ, valData)
            winreg.CloseKey(targetKey)
            return {"success": True, "error": None}
        except OSError as err:
            return {
                "success": False,
                "error": SharedErrors.FAILED_TO_WRITE,
                "errorObj": err,
            }

    def deleteRegistryValue(self, root, path, valName) -> DeleteValRet:
        openKeyRet = self.openKey(root, path)
        if not openKeyRet["success"] or not openKeyRet["data"]:
            return {"success": False, "error": openKeyRet["error"]}
        targetKey = openKeyRet["data"]
        try:
            winreg.DeleteValue(targetKey, valName)
            winreg.CloseKey(targetKey)
            return {"success": True, "error": None}
        except OSError as err:
            return {
                "success": False,
                "error": SharedErrors.FAILED_TO_WRITE,
                "errorObj": err,
            }

    def _deleteSubKeysRecursive(self, key):
        try:
            subKeyNames = []
            i = 0
            while True:
                try:
                    subKeyName = winreg.EnumKey(key, i)
                    subKeyNames.append(subKeyName)
                    i += 1
                except OSError:
                    break

            for subKeyName in subKeyNames:
                try:
                    subKey = winreg.OpenKey(key, subKeyName, 0, winreg.KEY_ALL_ACCESS)
                    self._deleteSubKeysRecursive(subKey)
                    winreg.CloseKey(subKey)
                    winreg.DeleteKey(key, subKeyName)
                except OSError:
                    continue

        except Exception:
            pass

    def deleteRegistryKey(self, root, path) -> DeleteKeyRet:
        try:
            openKeyRet = self.openKey(root, path)
            if not openKeyRet["success"] or not openKeyRet["data"]:
                return {"success": False, "error": openKeyRet["error"]}

            targetKey = openKeyRet["data"]

            self._deleteSubKeysRecursive(targetKey)

            winreg.CloseKey(targetKey)

            if len(path) > 0:
                parentPath = path[:-1]
                keyName = path[-1]

                if parentPath:
                    parentOpenRet = self.openKey(root, parentPath)
                    if parentOpenRet["success"] and parentOpenRet["data"]:
                        winreg.DeleteKey(parentOpenRet["data"], keyName)
                        winreg.CloseKey(parentOpenRet["data"])
                    else:
                        return {"success": False, "error": parentOpenRet["error"]}
                else:
                    winreg.DeleteKey(root, keyName)

            return {"success": True, "error": None}

        except OSError as err:
            return {
                "success": False,
                "error": SharedErrors.FAILED_TO_WRITE,
                "errorObj": err,
            }
        except Exception as err:
            return {
                "success": False,
                "error": SharedErrors.UNKNOWN_ERROR,
                "errorObj": err,
            }
