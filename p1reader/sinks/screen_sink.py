import logging

from dsmr_parser.objects import Telegram

from p1reader.sinks.data_sink import DataSink, DataSinkConfig

LOGGER = logging.getLogger(__name__)


class ScreenSinkConfig(DataSinkConfig):
    @property
    def output_stream(self) -> DataSink:
        return ScreenSink()


class ScreenSink(DataSink):
    def process_telegram(self, telegram: Telegram) -> None:
        print(telegram)
