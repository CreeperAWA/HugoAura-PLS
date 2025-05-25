import json
from typing import Any

from loguru import logger
from pydantic import BaseModel


class AuraPLSConfig(BaseModel):
    proxyProcArr: list[str]
    wsHost: str
    wsPort: int
    certPath: str
    keyPath: str
    ruleSettings: dict
    _configPath: str

    def __getitem__(self, key: Any) -> Any:
        return getattr(self, key)  # 支持一下通过 ["key"] 访问, 虽然不太规范...

    def __setitem__(self, key: Any, val: Any):
        if key not in self.model_fields:
            raise KeyError
        setattr(self, key, val)

    def saveConfig(self):
        if hasattr(self, "_configPath"):
            with open(self._configPath, "w") as f:
                json.dump(self.model_dump(), f, indent=2)
        else:
            logger.warning("Config path attr not found for AuraPLSConfig object.")
