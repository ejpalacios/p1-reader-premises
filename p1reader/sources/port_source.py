from dsmr_parser.clients import SERIAL_SETTINGS_V5, SerialReader
from dsmr_parser.telegram_specifications import BELGIUM_FLUVIUS

from p1reader.sources.data_source import DataSource


class PortSourceConfig(DataSource):
    id: str

    @property
    def input_stream(self) -> SerialReader:
        return SerialReader(
            device=self.id,
            serial_settings=SERIAL_SETTINGS_V5,
            telegram_specification=BELGIUM_FLUVIUS,
        )
