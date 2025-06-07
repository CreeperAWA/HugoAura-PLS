import json
import os
from pathlib import Path
import shutil
from loguru import logger
import lifecycle
from deepdiff import DeepDiff
from copy import deepcopy

from typeDefs.config import AuraPLSConfig


def mergeConfigs(defaultConfig: dict, userConfig: dict) -> dict:
    result = deepcopy(userConfig)

    for key, default_value in defaultConfig.items():
        if key not in result:
            result[key] = deepcopy(default_value)
        elif isinstance(default_value, dict) and isinstance(result[key], dict):
            result[key] = mergeConfigs(default_value, result[key])
        elif isinstance(default_value, list) and isinstance(result[key], list):
            if len(default_value) > len(result[key]):
                result[key].extend(deepcopy(default_value[len(result[key]) :]))

    return result


def loadConfig(
    configPath="config/user.json", defaultConfPath="config/default.json"
) -> AuraPLSConfig:
    os.makedirs(os.path.dirname(configPath), exist_ok=True)

    defaultConfigFullPath = Path.joinpath(
        Path("." if not lifecycle.meiPassDir else lifecycle.meiPassDir),
        Path(defaultConfPath),
    )

    try:
        with open(str(defaultConfigFullPath)) as f:
            defaultConfig = json.load(f)
    except FileNotFoundError:
        logger.error(f"Default config file not found at {defaultConfPath}")
        input("Press any key to continue...")
        raise

    try:
        with open(configPath) as f:
            userConfig = json.load(f)
            mergedConfig = mergeConfigs(defaultConfig, userConfig)
            config = AuraPLSConfig(**mergedConfig)
            if mergedConfig and DeepDiff(userConfig, mergedConfig):
                logger.warning("🚀 Migrating your config to a newer version ...")
                with open(configPath, "w") as f:
                    json.dump(mergedConfig, f, indent=2)
    except FileNotFoundError:
        logger.warning(
            "No user config file found, creating a new config using default.json ..."
        )
        shutil.copyfile(str(defaultConfigFullPath), configPath)
        with open(str(defaultConfigFullPath)) as f:
            config = AuraPLSConfig(**json.load(f))

    config._configPath = configPath
    lifecycle.appConfig = config

    return config
