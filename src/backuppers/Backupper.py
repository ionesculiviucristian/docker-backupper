from abc import ABC, abstractmethod
from typing import Callable, Generic, List, TypedDict, TypeVar, cast

from docker.models.containers import Container

from src.App import App
from src.backuppers.Docker import docker
from src.mirrors.FTP import FTP
from src.mirrors.RSync import RSync
from src.typehints import TypeConfigContainers


class TypeBackupperConfigProperty(TypedDict):
    local_storage_path: str
    mirror_storage_path: str


class TypeBackupServiceConfigParam(TypedDict):
    storage_path: str
    callback: Callable[[Container, str, str], bool]


T = TypeVar("T", bound=TypeConfigContainers)


class Backupper(ABC, Generic[T]):
    app: App
    containers: List[T]

    @property
    @abstractmethod
    def _type(self) -> str | None:
        pass

    @property
    @abstractmethod
    def config(self) -> TypeBackupperConfigProperty:
        pass

    @property
    @abstractmethod
    def subject(self) -> str:
        pass

    @abstractmethod
    def backup(self) -> bool:
        pass

    def __init__(self, app: App):
        self.app = app
        self.containers = cast(
            List[T],
            [container for container in app.config["containers"] if container and container["type"] == self._type],
        )

    def backup_service(self, callback: Callable[[T, Container, str], bool]) -> bool:
        if len(self.containers) == 0:
            self.app.notify_manager.send_warning(
                f"Backing up {self.subject} is disabled because no containers are defined"
            )
            return True

        has_errors = False

        backup_path = self.app.generate_backup_path(self.config["local_storage_path"])

        returncode, _, stderr = self.app.run_command(f'mkdir -p "{backup_path}"')
        if returncode != 0:
            self.app.notify_manager.send_error(stderr)
            return True

        self.app.notify_manager.send_action(f"Backing up {self.subject} to {backup_path}")

        for container in self.containers:
            if container is None:
                continue

            docker_container = docker.find_container(container["name"])
            if not docker_container:
                self.app.notify_manager.send_error(f"{container['name']} container not found", True)
                continue

            try:
                has_errors = callback(container, docker_container, backup_path)
            except Exception as ex:
                has_errors = True
                self.app.notify_manager.send_error(self.app.get_exception_trace(ex))

        return not has_errors

    @staticmethod
    def run_backupper(
        app: App,
        ftp: bool,
        ftp_only: bool,
        rsync: bool,
        rsync_only: bool,
        backupper: "Backupper[T]" | List["Backupper[T]"],
    ) -> None:
        backuppers = backupper if isinstance(backupper, List) else [backupper]

        app.notify_manager.send_time(
            f"Started backup at {app.get_current_datetime()} on {app.hostname} {app.external_ip}"
        )

        for _backupper in backuppers:
            if not ftp_only and not rsync_only:
                _backupper.backup()

            if ftp or ftp_only:
                for ftp_mirror in app.config["mirrors"]["ftp"]:
                    ftp_client = FTP(app, ftp_mirror)
                    ftp_client.connect()

                    app.notify_manager.send_action(
                        f"Transferring {_backupper.subject} to {ftp_mirror['host']} FTP mirror"
                    )

                    for source in app.get_backup_file_paths(_backupper.config["local_storage_path"]):
                        ftp_client.transfer(source, _backupper.config["mirror_storage_path"])

                    ftp_client.quit()

            if rsync or rsync_only:
                for rsync_mirror in app.config["mirrors"]["rsync"]:
                    rsync_client = RSync(app, rsync_mirror)
                    rsync_client.connect()

                    app.notify_manager.send_action(
                        f"Transferring {_backupper.subject} to {rsync_mirror['host']} to RSync mirror"
                    )

                    for source in app.get_backup_file_paths(_backupper.config["local_storage_path"]):
                        rsync_client.transfer(source, _backupper.config["mirror_storage_path"])

        app.notify_manager.send_time(f"Finished backup at {app.get_current_datetime()}")
        app.notify_manager.send_log_file()
