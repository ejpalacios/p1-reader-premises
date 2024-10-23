from abc import abstractproperty
from typing import Union

from dsmr_parser.clients import SerialReader
from dsmr_parser.clients.filereader import FileReader
from pydantic import BaseModel


class DataSource(BaseModel):
    """Base class for data sources"""

    @abstractproperty
    def input_stream(self) -> Union[SerialReader, FileReader]:
        """
        Instance of the input stream of the data  source

        Returns:
            Union[SerialReader, FileReader]: input stream
        """
