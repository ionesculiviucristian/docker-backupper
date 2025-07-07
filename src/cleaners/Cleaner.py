import re
from abc import ABC, abstractmethod
from datetime import datetime, time, timedelta
from typing import Generic, List, Optional, TypeVar

from src.App import App

TypeConfigCleaner = TypeVar("TypeConfigCleaner")


class Cleaner(ABC, Generic[TypeConfigCleaner]):
    app: App
    config: TypeConfigCleaner

    def __init__(self, app: App, config: TypeConfigCleaner):
        self.app = app
        self.config = config

    @abstractmethod
    def add_path(self, path: str, retention_days: Optional[int] = None) -> None:
        pass

    @abstractmethod
    def run(self) -> None:
        pass

    def get_removable_folders(self, path: str, folders: List[str], retention_days: int) -> List[str]:
        removable_folders: List[str] = []

        pattern = re.compile(r"\d{4}-\d{2}-\d{2}")

        today = datetime.combine(datetime.today().date(), time.min)
        threshold_date = today - timedelta(days=int(retention_days) - 1)

        for folder in folders:
            if pattern.match(folder):
                folder_date = datetime.strptime(folder, "%Y-%m-%d")

                if folder_date < threshold_date:
                    removable_folders.append(f"{path}/{folder}")

        removable_folders.sort()

        return removable_folders
