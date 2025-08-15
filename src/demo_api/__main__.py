from pathlib import Path

from demo_api.utils.config_schema import load_config
from demo_api.api.server import main


main(load_config(Path("config.toml")))
