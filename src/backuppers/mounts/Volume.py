from typing import TypedDict

from docker.models.containers import Container
from docker.types.services import Mount

from src.backuppers.Backupper import Backupper, TypeBackupperConfigProperty
from src.backuppers.Docker import docker


class TypeVolumeInfo(TypedDict):
    container: Container
    attrs: Mount


class Volume(Backupper[None]):
    @property
    def _type(self) -> None:
        return None

    @property
    def config(self) -> TypeBackupperConfigProperty:
        return {
            "local_storage_path": self.app.config["mounts"]["storage_path"],
            "mirror_storage_path": "mounts",
        }

    @property
    def subject(self) -> str:
        return "Docker volume mounts"

    def backup(self) -> bool:
        if len(self.app.config["mounts"]["volumes"]) == 0:
            self.app.notify_manager.send_warning(
                f"Backing up {self.subject} is disabled because no entries are defined"
            )
            return True

        has_errors = False

        backup_path = self.app.generate_backup_path(self.app.config["mounts"]["storage_path"])

        returncode, _, stderr = self.app.run_command(f'mkdir -p "{backup_path}"')
        if returncode != 0:
            self.app.notify_manager.send_error(stderr)
            return True

        self.app.notify_manager.send_action(f"Backing up {self.subject} to {backup_path}")

        for volume in self.app.config["mounts"]["volumes"]:
            result = docker.find_volume(volume)

            if not result:
                self.app.notify_manager.send_error(f"{volume} mount not found", True)
                has_errors = True
                continue

            mount, container = result

            try:
                self.__backup_mount(mount, container, backup_path)
                self.app.notify_manager.send_success(f"{volume}: backed up successfully", True)
            except Exception as ex:
                has_errors = True
                self.app.notify_manager.send_error(f"{volume}: {self.app.get_exception_trace(ex)}", True)

        return not has_errors

    def __backup_mount(self, mount: Mount, container: Container, path: str) -> None:
        docker.backup_volume(
            f"{self.app.backup_prefix}_{container.name}_{mount['Name']}",
            mount["Source"],
            path,
        )
