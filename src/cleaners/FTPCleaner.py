from typing import List, Optional, Tuple

from src.App import App
from src.cleaners.Cleaner import Cleaner
from src.mirrors import FTP
from src.typehints import TypeConfigMirrorFTP


class FTPCleaner(Cleaner[TypeConfigMirrorFTP]):
    ftp: FTP
    paths: List[Tuple[str, int]]

    def __init__(self, app: App, config: TypeConfigMirrorFTP) -> None:
        super().__init__(app, config)
        self.ftp = FTP(self.app, self.config)
        self.ftp.connect()
        self.paths = []

    def add_path(self, path: str, retention_days: Optional[int] = None) -> None:
        self.paths.append((path, retention_days if retention_days else self.config["retention_days"]))

    def run(self) -> None:
        if len(self.paths) == 0:
            self.app.notify_manager.send_warning("No paths set when running FTP cleaning", True)
            return

        for path, retention_days in self.paths:
            self.__remove_backups(path, retention_days)

    def __remove_backups(self, path: str, retention_days: int) -> None:
        removable_paths = self.get_removable_folders(path, self.ftp.list_items(path), retention_days)

        if len(removable_paths) == 0:
            self.app.notify_manager.send_info(f"No backups older than {retention_days} days found in {path}", True)
            return

        self.app.notify_manager.send_action(f"Removing backups older than {retention_days} days from {path}", True)

        for removable_path in removable_paths:
            try:
                self.ftp.remove_path_items(removable_path)
                self.app.notify_manager.send_success(f"{removable_path}: removed successfully", True)
            except Exception as ex:
                self.app.notify_manager.send_error(f"{removable_path}: {str(ex)}", True)
