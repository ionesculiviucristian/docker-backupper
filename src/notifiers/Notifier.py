from abc import ABC, abstractmethod
from typing import Callable, Tuple, TypedDict

from src.loggers.LogManager import LogManager
from src.typehints import TypeConfig


class TypeContructorHelpersParam(TypedDict):
    get_external_ip: Callable[[], Tuple[str, str]]


class Notifier(ABC):
    config: TypeConfig
    log_manager: LogManager

    def __init__(self, config: TypeConfig, log_manager: LogManager, helpers: TypeContructorHelpersParam):
        self.config = config
        self.log_manager = log_manager
        self.helpers = helpers

    @abstractmethod
    def send_log_file(self, path: str) -> bool:
        pass

    @abstractmethod
    def send_message(self, message: str) -> bool:
        pass
