import logging
import os
from datetime import datetime

from src.loggers.Logger import Logger
from src.typehints import TypeConfig


class FileLogger(Logger):
    log_path: str
    logger: logging.Logger

    def __init__(self, config: TypeConfig) -> None:
        super().__init__(config)
        self.log_path = os.path.join(
            self.config["logs"]["path"], f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
        )
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

        file_handler = logging.FileHandler(self.log_path)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(self.config["logs"]["level"])
        self.logger.addHandler(console_handler)

    def log(self, message: str, level: int = logging.INFO) -> None:
        if level == logging.DEBUG:
            self.logger.debug(message)
        elif level == logging.INFO:
            self.logger.info(message)
        elif level == logging.WARNING:
            self.logger.warning(message)
        elif level == logging.ERROR:
            self.logger.error(message)
        elif level == logging.CRITICAL:
            self.logger.critical(message)
