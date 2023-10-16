from pathlib import Path

import pytest

from p1reader.sinks import ScreenSink, ScreenSinkConfig
from p1reader.sources import FileSourceConfig


def test_screen_sink_config(
    file_source: FileSourceConfig, screen_sink: ScreenSinkConfig
) -> None:
    assert type(screen_sink.output_stream) == ScreenSink
    source = file_source.input_stream
    for telegram in source.read_as_object():
        screen_sink.output_stream.process_telegram(telegram)
