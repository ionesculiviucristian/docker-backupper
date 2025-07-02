import logging

from src.loggers.FileLogger import FileLogger
from src.typehints import TypeConfig


class LogManager:
    config: TypeConfig
    file_logger: FileLogger

    def __init__(self, config: TypeConfig):
        self.config = config
        self.file_logger = FileLogger(self.config)

    def info(self, message: str) -> str:
        return self.__log(message, logging.INFO)

    def warning(self, message: str) -> str:
        return self.__log(message, logging.WARNING)

    def error(self, message: str) -> str:
        return self.__log(message, logging.ERROR)

    def debug(self, message: str) -> str:
        return self.__log(message, logging.DEBUG)

    def __log(self, message: str, log_level: int = logging.NOTSET) -> str:
        self.file_logger.log(message, log_level)
        return message
