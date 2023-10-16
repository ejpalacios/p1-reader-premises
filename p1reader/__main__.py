import argparse
import logging
import os

import yaml

from p1reader.service import ReaderService, ReaderServiceConfig

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "DEBUG"),
    format="[%(asctime)s] - %(levelname) -8s| %(name)s:%(funcName)s => %(message)s",
)
LOGGER = logging.getLogger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reader service")
    parser.add_argument(
        "--config",
        help="Path to YAML configuration file",
    )

    args = parser.parse_args()
    config = None
    if args.config:
        with open(args.config) as f:
            config = ReaderServiceConfig(**yaml.load(f, Loader=yaml.FullLoader))
    else:
        config = ReaderServiceConfig()

    LOGGER.info(f"Running service")
    ReaderService(config.input_stream, config.output_streams).run()
