import logging
from pathlib import Path

from dsmr_parser.objects import Telegram

from p1reader.sinks.data_sink import DataSink, DataSinkConfig

LOGGER = logging.getLogger(__name__)


class FileSinkConfig(DataSinkConfig):
    file: Path

    @property
    def output_stream(self) -> DataSink:
        return FileSink(self.file)


class FileSink(DataSink):
    def __init__(self, output_file: Path) -> None:
        self._output_file = output_file

    def process_telegram(self, telegram: Telegram) -> None:
        with open(self._output_file, "a") as f:
            f.write(telegram.to_json())
            f.write("\n")
