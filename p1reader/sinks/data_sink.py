from abc import abstractmethod, abstractproperty

from dsmr_parser.objects import Telegram
from pydantic import BaseModel


class DataSink:
    @abstractmethod
    def process_telegram(self, telegram: Telegram) -> None:
        pass


class DataSinkConfig(BaseModel):
    @abstractproperty
    def output_stream(self) -> DataSink:
        pass
