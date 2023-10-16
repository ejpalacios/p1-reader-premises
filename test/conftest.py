from pathlib import Path

import pytest

from p1reader.sinks import DBSinkConfig, ScreenSinkConfig
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
def screen_sink() -> ScreenSinkConfig:
    return ScreenSinkConfig()
