from abc import ABC, abstractmethod


class Logger(ABC):
    @abstractmethod
    def log(self, message: str, level: int) -> None:
        pass
