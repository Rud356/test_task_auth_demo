from pathlib import Path

from demo_api.utils.config_schema import load_config


print(load_config(Path("config.toml")))