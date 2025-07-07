import os
from ftplib import FTP as FTPlib
from typing import List

from tqdm import tqdm

from src.App import App
from src.mirrors.Mirror import Mirror
from src.typehints import TypeConfigMirrorFTP


class FTP(Mirror[TypeConfigMirrorFTP]):
    client: FTPlib

    def __init__(self, app: App, config: TypeConfigMirrorFTP) -> None:
        super().__init__(app, config)
        self.client = FTPlib()

    def connect(self) -> None:
        self.client.connect(self.config["host"], int(self.config["config"]["port"]))
        self.client.login(self.config["config"]["username"], self.config["config"]["password"])

        self.app.log_manager.info(f"Established connection to FTP mirror at {self.config['host']}")

    def list_items(self, path: str) -> List[str]:
        items: List[str] = []

        self.app.log_manager.debug(f"cwd {path}")
        self.client.cwd(path)
        self.client.retrlines("LIST", lambda x: items.append(x.split()[-1]))

        return items

    def remove_path_items(self, path: str) -> None:
        for item in self.list_items(path=path):
            if item not in (".", ".."):
                try:
                    self.remove_path_items(f"{path}/{item}")
                except Exception:
                    self.app.log_manager.debug(f"delete {item}")
                    self.client.delete(item)

        self.app.log_manager.debug("cwd ..")
        self.client.cwd("..")

        self.app.log_manager.debug(f"rmd {path}")
        self.client.rmd(path)

    def transfer(self, source: str, destination: str) -> bool:
        destination = self.app.generate_backup_path(f"{self.config['storage_path']}/{destination}")

        if not self.__create_destination_path(destination):
            self.app.notify_manager.send_error(f"Unable to create destination path at {destination}")
            return False

        destination = f"{destination}/{source.split('/')[-1]}"

        if self.__transfer_file(source, destination):
            self.app.notify_manager.send_success(f"Transferred {source} to {destination}")
            return True
        else:
            self.app.notify_manager.send_error(f"Unable to transfer {source} to {destination}")
            return False

    def quit(self) -> None:
        self.client.quit()

    def __create_destination_path(self, path: str) -> bool:
        current_path = "/"
        self.app.log_manager.debug(f"cwd {current_path}")
        self.client.cwd(current_path)
        parts = path.split("/")[1:]

        try:
            for part in parts:
                try:
                    current_path += f"{part}/"
                    self.app.log_manager.debug(f"cwd {current_path}")
                    self.client.cwd(current_path)
                except Exception:
                    self.app.log_manager.debug(f"mkd {current_path}")
                    self.client.mkd(current_path)
            return True
        except Exception:
            return False

    def __transfer_file(self, source: str, destination: str) -> bool:
        try:
            with open(source, "rb") as stream:
                with tqdm(
                    unit="B",
                    unit_scale=True,
                    leave=False,
                    miniters=1,
                    desc=f"Transferring {source}...",
                    total=os.path.getsize(source),
                ) as tqdm_instance:
                    self.client.storbinary(
                        f"STOR {destination}",
                        stream,
                        2048,
                        callback=lambda sent: tqdm_instance.update(len(sent)),
                    )
                return True
        except Exception:
            return False
