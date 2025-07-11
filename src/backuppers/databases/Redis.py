import re

from docker.models.containers import Container

from src.backuppers.Backupper import Backupper, TypeBackupperConfigProperty
from src.backuppers.Docker import docker
from src.typehints import TypeConfigContainerRedis


class Redis(Backupper[TypeConfigContainerRedis]):
    @property
    def _type(self) -> str:
        return "redis"

    @property
    def config(self) -> TypeBackupperConfigProperty:
        return {
            "local_storage_path": self.app.config["container_types"]["redis"]["storage_path"],
            "mirror_storage_path": "redis",
        }

    @property
    def subject(self) -> str:
        return "Redis data"

    def backup(self) -> bool:
        def callback(container: TypeConfigContainerRedis, docker_container: Container, backup_path: str) -> bool:
            has_errors = False

            self.app.notify_manager.send_info(f"Starting backup for {container['name']} container", True)

            try:
                self.__export_container_database(container, docker_container, backup_path)
                self.app.notify_manager.send_success(f"{self.subject}: backed up successfully", True)
            except Exception as ex:
                has_errors = True
                self.app.notify_manager.send_error(f"{self.subject}: {self.app.get_exception_trace(ex)}", True)

            return has_errors

        return self.backup_service(callback)

    def __export_container_database(
        self, container: TypeConfigContainerRedis, docker_container: Container, path: str
    ) -> None:
        backup_file = f"{self.app.backup_prefix}_{container['name']}_data.tar.gz"

        command = f"""
        sh -c '
            set -eu;
            redis-cli -a {container['config']['password']} SAVE;
        '
        """

        exit_code, output = docker.container_exec(docker_container, command, redactor=Redis.__redact_command)

        if exit_code != 0:
            raise Exception(f"Unable to save {self.subject} from {container['name']} container: {output}")

        returncode, _, _ = self.app.run_command(f'docker cp "{docker_container.id}:/data/dump.rdb" {path}')
        if returncode != 0:
            raise Exception(f"Unable to copy {self.subject} from {container['name']} container to {path}")

        returncode, _, _ = self.app.run_command(f"tar -czf {path}/{backup_file} -C {path} dump.rdb")
        if returncode != 0:
            raise Exception(f"Unable to create {path}/{backup_file} file")

        returncode, _, _ = self.app.run_command(f"rm -rf {path}/dump.rdb")
        if returncode != 0:
            self.app.log_manager.warning(f"Unable to remove {path}/dump.rdb file")

    @staticmethod
    def __redact_command(command: str) -> str:
        return re.sub(r"(redis-cli -a )[^\s]+", r"\1****", command)
