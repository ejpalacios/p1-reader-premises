import pytest
from dsmr_parser.clients import SerialReader
from dsmr_parser.clients.filereader import FileReader

from p1reader.service import ReaderServiceConfig
from p1reader.sinks import ScreenSink
from p1reader.sources import FileSourceConfig, PortSourceConfig


def test_reader_service_config(
    file_source: FileSourceConfig, port_source: PortSourceConfig
) -> None:
    base_reader = ReaderServiceConfig()
    with pytest.raises(ValueError) as e_info:
        base_reader.input_stream

    file_reader = ReaderServiceConfig(file=file_source)
    assert type(file_reader.input_stream) == FileReader
    assert len(file_reader.output_streams) == 1
    assert type(file_reader.output_streams[0]) == ScreenSink

    port_reader = ReaderServiceConfig(port=port_source)
    assert type(port_reader.input_stream) == SerialReader
    assert len(port_reader.output_streams) == 1
    assert type(port_reader.output_streams[0]) == ScreenSink
