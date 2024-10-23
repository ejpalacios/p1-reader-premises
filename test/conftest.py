from pathlib import Path

import pytest

from p1reader.sinks import (
    DBSinkConfig,
    FileSinkConfig,
    MQTTSinkConfig,
    ScreenSinkConfig,
)
from p1reader.sources import FileSourceConfig, PortSourceConfig

file_path = "./data/test.txt"
port_id = "/dev/ttyUSB0"


@pytest.fixture(scope="module")
def file_source() -> FileSourceConfig:
    return FileSourceConfig(path=Path.cwd().joinpath(file_path))


@pytest.fixture(scope="module")
def port_source() -> PortSourceConfig:
    return PortSourceConfig(id=port_id)


@pytest.fixture(scope="module")
def screen_sink_config() -> ScreenSinkConfig:
    return ScreenSinkConfig()


@pytest.fixture(scope="module")
def mqtt_sink_config() -> MQTTSinkConfig:
    return MQTTSinkConfig(host="localhost")


@pytest.fixture(scope="module")
def db_sink_config() -> DBSinkConfig:
    return DBSinkConfig(host="localhost")


@pytest.fixture(scope="module")
def file_sink_config() -> FileSinkConfig:
    return FileSinkConfig(file=Path("./data/dump.json"))
