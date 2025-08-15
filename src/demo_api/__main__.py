import argparse
from pathlib import Path

from demo_api.fake_data_setup import setup_fake_data
from demo_api.utils.config_schema import AppConfig, load_config
from demo_api.api.server import main

parser: argparse.ArgumentParser = argparse.ArgumentParser(
    prog="demo_api",
    add_help=True,
    description="Hosts a web server with demo resource management api"
)
parser.add_argument(
    "--create-demo-data",
    default=False,
    action="store_true",
    dest="create_data"
)

config: AppConfig = load_config(Path("config.toml"))
args: argparse.Namespace = parser.parse_args()

if args.create_data:
    setup_fake_data(config)

else:
    main(config)
