import logging
from typing import Callable, Tuple, TypedDict

from src.loggers.LogManager import LogManager
from src.notifiers.Email import Email
from src.notifiers.Mattermost import Mattermost
from src.typehints import TypeConfig


class TypeContructorHelpersParam(TypedDict):
    get_external_ip: Callable[[], Tuple[str, str]]


class NotifyManager:
    padding_symbol: str = "• "

    config: TypeConfig
    log_manager: LogManager
    helpers: TypeContructorHelpersParam

    email: Email
    mattermost: Mattermost

    def __init__(self, config: TypeConfig, log_manager: LogManager, helpers: TypeContructorHelpersParam):
        self.config = config
        self.helpers = helpers
        self.log_manager = log_manager

        self.email = Email(self.config, self.log_manager, self.helpers)
        self.mattermost = Mattermost(self.config, self.log_manager, self.helpers)

    def send_action(self, message: str, padded: bool = False) -> None:
        self.log_manager.info(message)
        self.__send(f"{self.__get_padding(padded=padded)}🚀 {message}")

    def send_cleanup(self, message: str, padded: bool = False) -> None:
        self.log_manager.info(message)
        self.__send(f"{self.__get_padding(padded=padded)}🧹 {message}")

    def send_connect(self, message: str, padded: bool = False) -> None:
        self.log_manager.info(message)
        self.__send(f"{self.__get_padding(padded=padded)}🌍 {message}")

    def send_connect_local(self, message: str, padded: bool = False) -> None:
        self.log_manager.info(message)
        self.__send(f"{self.__get_padding(padded=padded)}🖥️ {message}")

    def send_error(self, message: str, padded: bool = False) -> None:
        self.log_manager.error(message)
        self.__send(f"{self.__get_padding(padded=padded)}🚨 {message}", logging.ERROR)

    def send_info(self, message: str, padded: bool = False) -> None:
        self.log_manager.info(message)
        self.__send(f"{self.__get_padding(padded=padded)}ℹ️ {message}")

    def send_success(self, message: str, padded: bool = False) -> None:
        self.log_manager.info(message)
        self.__send(f"{self.__get_padding(padded=padded)}✅ {message}")

    def send_time(self, message: str, padded: bool = False) -> None:
        self.log_manager.info(message)
        self.__send(f"{self.__get_padding(padded=padded)}🕒 {message}")

    def send_warning(self, message: str, padded: bool = False) -> None:
        self.log_manager.warning(message)
        self.__send(f"{self.__get_padding(padded=padded)}⚠️ {message}", logging.WARNING)

    def send_log_file(self) -> None:
        if self.config["notifiers"]["mattermost"]["active"]:
            self.mattermost.send_log_file(self.log_manager.file_logger.log_path)
        if self.config["notifiers"]["email"]["active"]:
            self.email.send_log_file(self.log_manager.file_logger.log_path)

    def __get_padding(self, padded: bool) -> str:
        return self.padding_symbol if padded else ""

    def __send(self, message: str, log_level: int = logging.NOTSET) -> None:
        if self.config["notifiers"]["mattermost"]["active"]:
            self.mattermost.send_message(message)
        if self.config["notifiers"]["email"]["active"] and log_level == logging.ERROR:
            self.email.send_message(message)
