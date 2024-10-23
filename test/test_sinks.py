from pathlib import Path

from p1reader.sinks import (
    DBSink,
    DBSinkConfig,
    FileSink,
    FileSinkConfig,
    MQTTSink,
    MQTTSinkConfig,
    ScreenSink,
    ScreenSinkConfig,
)
from p1reader.sources import FileSourceConfig


def test_screen_sink_config(
    file_source: FileSourceConfig, screen_sink_config: ScreenSinkConfig
) -> None:
    screen_sink = screen_sink_config.output_stream
    assert type(screen_sink) == ScreenSink
    source = file_source.input_stream
    for telegram in source.read_as_object():
        screen_sink.process_telegram(telegram)


def test_mqtt_sink_config(
    file_source: FileSourceConfig, mqtt_sink_config: MQTTSinkConfig
) -> None:
    mqtt_sink = mqtt_sink_config.output_stream
    assert type(mqtt_sink) == MQTTSink
    source = file_source.input_stream
    for telegram in source.read_as_object():
        mqtt_sink.process_telegram(telegram)


def test_db_sink_config(
    file_source: FileSourceConfig, db_sink_config: DBSinkConfig
) -> None:
    db_sink = db_sink_config.output_stream
    assert type(db_sink) == DBSink
    source = file_source.input_stream
    for telegram in source.read_as_object():
        db_sink.process_telegram(telegram)


def test_file_sink_config(
    file_source: FileSourceConfig, file_sink_config: FileSinkConfig
) -> None:
    file_sink = file_sink_config.output_stream
    assert type(file_sink) == FileSink
    source = file_source.input_stream
    for telegram in source.read_as_object():
        file_sink.process_telegram(telegram)
    output_file: Path = file_sink._output_file
    assert output_file.is_file() == True
    output_file.unlink()
