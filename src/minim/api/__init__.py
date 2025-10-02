import yaml

from .. import CONFIG_FILE, config

__all__ = ["spotify"]

if "api" in config:
    api_config = config["api"]
else:
    config["api"] = api_config = {"api": {}}
    with CONFIG_FILE.open("w") as f:
        yaml.safe_dump(config, f)
