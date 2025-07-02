import datetime
import os
import re
import socket
import subprocess
import time
import traceback
from typing import Callable, List, Optional, Tuple

import requests

from src.config import config
from src.loggers.LogManager import LogManager
from src.notifiers.NotifyManager import NotifyManager
from src.typehints import TypeConfig


class App:
    backup_prefix: str

    config: TypeConfig
    log_manager: LogManager
    notify_manager: NotifyManager

    hostname: str
    external_ip: str

    def __init__(self) -> None:
        self.backup_prefix = f"{int(time.time())}_{datetime.datetime.now().strftime('%Y_%m_%d')}"

        self.config = config
        self.log_manager = LogManager(self.config)
        self.notify_manager = NotifyManager(
            self.config, self.log_manager, {"get_external_ip": lambda: self.get_external_ip()}
        )

        self.hostname, self.external_ip = self.get_external_ip()

    def run_command(self, command: str, redactor: Optional[Callable[[str], str]] = None) -> Tuple[int, str, str]:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        stdout = result.stdout.decode("utf-8", errors="ignore").strip()
        stderr = result.stderr.decode("utf-8", errors="ignore").strip()

        command = re.sub(r"\s+", " ", command).strip()
        command = redactor(command) if redactor else command

        self.log_manager.debug(
            f"Command `{command}` returned `{result.returncode}` code with stdout `{stdout}` and stderr `{stderr}`"
        )

        return result.returncode, stdout, stderr

    def get_external_ip(self) -> Tuple[str, str]:
        hostname = socket.gethostname()

        try:
            response = requests.get("https://api.ipify.org?format=json")
            response.raise_for_status()

            return hostname, response.json()["ip"]
        except Exception as e:
            self.log_manager.warning(f"Unable to obtain external IP: {str(e)}")

            return hostname, socket.gethostbyname(hostname)

    def generate_backup_path(self, path: str) -> str:
        path = path.replace("~", self.get_user_home_path())

        return f'{path}/{datetime.datetime.now().strftime("%Y-%m-%d")}'

    def get_backup_file_paths(self, path: str) -> List[str]:
        backup_file_paths: List[str] = []

        backup_path = self.generate_backup_path(path)

        if os.path.exists(backup_path) and os.path.isdir(backup_path):
            for root, _, files in os.walk(backup_path):
                for file in files:
                    file_path = os.path.join(root, file)

                    backup_file_paths.append(file_path)
            return backup_file_paths
        else:
            return []

    @staticmethod
    def get_current_datetime() -> str:
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_user_home_path() -> str:
        return os.path.expanduser("~")

    @staticmethod
    def get_exception_trace(ex: Exception) -> str:
        return "".join(traceback.format_exception(type(ex), ex, ex.__traceback__))


app = App()
