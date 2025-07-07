from abc import ABC, abstractmethod

from src.typehints import TypeConfig


class Logger(ABC):
    config: TypeConfig

    def __init__(self, config: TypeConfig) -> None:
        self.config = config

    @abstractmethod
    def log(self, message: str, level: int) -> None:
        pass
