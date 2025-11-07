import yaml

from .. import CONFIG_YAML_FILE, config

if "gui" in config:
    gui_config = config["gui"]
else:
    config["gui"] = gui_config = {"library": {}}
    with CONFIG_YAML_FILE.open("w") as f:
        yaml.safe_dump(config, f)
