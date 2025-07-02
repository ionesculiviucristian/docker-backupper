import os
from typing import List, Optional, Tuple

from src.App import App
from src.cleaners.Cleaner import Cleaner


class LocalCleaner(Cleaner):
    app: App
    paths: List[Tuple[str, int]]

    def __init__(self, app: App) -> None:
        self.app = app
        self.paths = []

    def add_path(self, path: str, time_to_keep: Optional[int] = None) -> None:
        self.paths.append((path, time_to_keep if time_to_keep else self.app.config["cleaning_interval"]))

    def run(self) -> None:
        if len(self.paths) == 0:
            self.app.notify_manager.send_warning("No paths set when running local cleaning", True)
            return

        for path, time_to_keep in self.paths:
            self.__remove_backups(path, time_to_keep)

    def __get_removable_folders(self, path: str, time_to_keep: int) -> List[str]:
        folders: List[str] = []

        if os.path.exists(path):
            for folder in os.listdir(path):
                folder_path = os.path.join(path, folder)

                if os.path.isdir(folder_path):
                    folders.append(folder_path)

        return self.get_removable_folders(path, folders, time_to_keep)

    def __remove_backups(self, path: str, time_to_keep: int) -> None:
        removable_paths = self.__get_removable_folders(path, time_to_keep)

        if len(removable_paths) == 0:
            self.app.notify_manager.send_action(f"No backups older than {time_to_keep} days found in {path}", True)
            return

        self.app.notify_manager.send_action(f"Removing backups older than {time_to_keep} days from {path}", True)

        for removable_path in removable_paths:
            try:
                self.app.run_command(f"rm -rf {removable_path}")
                self.app.notify_manager.send_success(f"{removable_path}: removed successfully", True)
            except Exception as ex:
                self.app.notify_manager.send_error(f"{removable_path}: {str(ex)}", True)
