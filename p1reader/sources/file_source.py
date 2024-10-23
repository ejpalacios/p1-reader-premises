from pathlib import Path

from dsmr_parser.clients.filereader import FileReader
from dsmr_parser.telegram_specifications import BELGIUM_FLUVIUS

from p1reader.sources.data_source import DataSource


class FileSourceConfig(DataSource):
    path: Path

    @property
    def input_stream(self) -> FileReader:
        return FileReader(
            file=self.path,
            telegram_specification=BELGIUM_FLUVIUS,
        )
