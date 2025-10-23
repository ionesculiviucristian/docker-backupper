from pathlib import Path

from src.backuppers.Backupper import Backupper, TypeBackupperConfigProperty
from src.backuppers.Docker import docker
from src.typehints import TypeConfigMountBindContainer, TypeConfigMountBindContainerPath


class Bind(Backupper[None]):
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
        return "Docker bind mounts"

    def is_backup_disabled(self):
        return len(self.app.config["mounts"]["binds"]) == 0

    def backup(self) -> bool:
        if self.is_backup_disabled():
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

        for container in self.app.config["mounts"]["binds"]["containers"]:
            for path in container["paths"]:
                if not Path(path["path"]).exists():
                    self.app.notify_manager.send_error(f"Bind mount {path['path']} not found")
                    has_errors = True
                    continue

                try:
                    self.__backup_mount(container, path, backup_path)
                    self.app.notify_manager.send_success(f"{path['path']}: backed up successfully", True)
                except Exception as ex:
                    has_errors = True
                    self.app.notify_manager.send_error(f"{path['path']}: {self.app.get_exception_trace(ex)}", True)

        return not has_errors

    def __backup_mount(
        self, container: TypeConfigMountBindContainer, path: TypeConfigMountBindContainerPath, backup_path: str
    ) -> None:
        docker.backup_volume(
            f"{self.app.backup_prefix}_{container['name']}_{path['name']}",
            path["path"],
            backup_path,
        )
