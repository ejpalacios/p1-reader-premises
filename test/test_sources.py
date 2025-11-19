from pathlib import Path

from dsmr_parser.clients import SerialReader
from dsmr_parser.clients.filereader import FileReader
from dsmr_parser.telegram_specifications import BELGIUM_FLUVIUS

from p1reader.sources import FileSourceConfig, PortSourceConfig

from .conftest import file_path, port_id


def test_file_source_config(file_source: FileSourceConfig) -> None:
    assert file_source.path == Path.cwd().joinpath(file_path)
    assert isinstance(file_source.input_stream, FileReader)
    assert file_source.input_stream.telegram_specification == BELGIUM_FLUVIUS


def test_port_source_config(port_source: PortSourceConfig) -> None:
    assert port_source.id == port_id
    assert isinstance(port_source.input_stream, SerialReader)
    assert port_source.input_stream.telegram_specification == BELGIUM_FLUVIUS
