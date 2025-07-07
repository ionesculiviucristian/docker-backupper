import os
from typing import List, Optional, Tuple

from src.App import App
from src.cleaners.Cleaner import Cleaner
from src.typehints import TypeConfig


class LocalCleaner(Cleaner[TypeConfig]):
    paths: List[Tuple[str, int]]

    def __init__(self, app: App, config: TypeConfig) -> None:
        super().__init__(app, config)
        self.paths = []

    def add_path(self, path: str, retention_days: Optional[int] = None) -> None:
        self.paths.append((path, retention_days if retention_days else self.config["retention_days"]))

    def run(self) -> None:
        if len(self.paths) == 0:
            self.app.notify_manager.send_warning("No paths set when running local cleaning", True)
            return

        for path, retention_days in self.paths:
            self.__remove_backups(path, retention_days)

    def __get_removable_folders(self, path: str, retention_days: int) -> List[str]:
        folders: List[str] = []

        if os.path.exists(path):
            for folder in os.listdir(path):
                folder_path = os.path.join(path, folder)

                if os.path.isdir(folder_path):
                    folders.append(folder_path)

        return self.get_removable_folders(path, folders, retention_days)

    def __remove_backups(self, path: str, retention_days: int) -> None:
        removable_paths = self.__get_removable_folders(path, retention_days)

        if len(removable_paths) == 0:
            self.app.notify_manager.send_action(f"No backups older than {retention_days} days found in {path}", True)
            return

        self.app.notify_manager.send_action(f"Removing backups older than {retention_days} days from {path}", True)

        for removable_path in removable_paths:
            try:
                self.app.run_command(f"rm -rf {removable_path}")
                self.app.notify_manager.send_success(f"{removable_path}: removed successfully", True)
            except Exception as ex:
                self.app.notify_manager.send_error(f"{removable_path}: {str(ex)}", True)
