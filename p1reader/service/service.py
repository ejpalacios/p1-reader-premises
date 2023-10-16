from abc import abstractmethod


class Service:
    @abstractmethod
    def run(self) -> None:
        """
        Start service
        """
