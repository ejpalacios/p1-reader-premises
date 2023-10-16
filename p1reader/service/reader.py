import logging
from typing import Optional, Union

from dsmr_parser.clients import SerialReader
from dsmr_parser.clients.filereader import FileReader
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from p1reader.service.service import Service
from p1reader.sinks import (
    DBSinkConfig,
    FileSinkConfig,
    MQTTSinkConfig,
    ScreenSinkConfig,
)
from p1reader.sinks.data_sink import DataSink
from p1reader.sources import FileSourceConfig, PortSourceConfig

LOGGER = logging.getLogger(__name__)


class ReaderServiceConfig(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    db: Optional[DBSinkConfig] = None
    mqtt: Optional[MQTTSinkConfig] = None
    dump: Optional[FileSinkConfig] = None
    port: Optional[PortSourceConfig] = None
    file: Optional[FileSourceConfig] = None

    @property
    def input_stream(self) -> Union[FileReader, SerialReader]:
        input = None
        if self.port is not None:
            LOGGER.debug(f"Using port source {self.port}")
            input = self.port.input_stream
        elif self.file is not None:
            LOGGER.debug(f"Using file source {self.file}")
            input = self.file.input_stream
        else:
            raise ValueError("Either a port of a file data source must be supplied")
        return input

    @property
    def output_streams(self) -> list[DataSink]:
        outputs = []
        if self.dump is not None:
            outputs.append(self.dump.output_stream)
        if self.db is not None:
            outputs.append(self.db.output_stream)
        if self.mqtt is not None:
            outputs.append(self.mqtt.output_stream)
        if len(outputs) == 0:
            outputs.append(ScreenSinkConfig().output_stream)

        return outputs


class ReaderService(Service):
    def __init__(
        self,
        input_stream: Union[FileReader, SerialReader],
        output_streams: list[DataSink],
    ) -> None:
        self._input_stream = input_stream
        self._output_streams = output_streams

    def run(self) -> None:
        try:
            for telegram in self._input_stream.read_as_object():
                LOGGER.debug(
                    f"Parsed telegram at {telegram.P1_MESSAGE_TIMESTAMP.value}"
                )
                LOGGER.debug(telegram.to_json())
                for output_stream in self._output_streams:
                    output_stream.process_telegram(telegram)
        except KeyboardInterrupt:
            LOGGER.info(f"Stopped reading telegrams")
        except UnicodeDecodeError as e:
            LOGGER.error(f"Decoding Error: {e}")
        except Exception as e:
            LOGGER.error(e)
