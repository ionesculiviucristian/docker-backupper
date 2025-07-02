import re
from abc import ABC, abstractmethod
from datetime import datetime, time, timedelta
from typing import List, Optional

from src.App import App


class Cleaner(ABC):
    app: App

    def __init__(self, app: App):
        self.app = app

    @abstractmethod
    def add_path(self, path: str, time_to_keep: Optional[int] = None) -> None:
        pass

    @abstractmethod
    def run(self) -> None:
        pass

    def get_removable_folders(self, path: str, folders: List[str], time_to_keep: int) -> List[str]:
        removable_folders: List[str] = []

        pattern = re.compile(r"\d{4}-\d{2}-\d{2}")

        today = datetime.combine(datetime.today().date(), time.min)
        threshold_date = today - timedelta(days=int(time_to_keep) - 1)

        for folder in folders:
            if pattern.match(folder):
                folder_date = datetime.strptime(folder, "%Y-%m-%d")

                if folder_date < threshold_date:
                    removable_folders.append(f"{path}/{folder}")

        removable_folders.sort()

        return removable_folders
