from docker.models.containers import Container

from src.backuppers.Backupper import Backupper, TypeBackupperConfigProperty
from src.backuppers.Docker import docker
from src.typehints import TypeConfigContainerGitlab


class GitLab(Backupper[TypeConfigContainerGitlab]):
    @property
    def _type(self) -> str:
        return "gitlab"

    @property
    def config(self) -> TypeBackupperConfigProperty:
        return {
            "local_storage_path": self.app.config["container_types"]["gitlab"]["storage_path"],
            "mirror_storage_path": "gitlab",
        }

    @property
    def subject(self) -> str:
        return "GitLab config and data"

    def backup(self) -> bool:
        def callback(_: TypeConfigContainerGitlab, docker_container: Container, backup_path: str) -> bool:
            has_errors = False

            try:
                self.__backup_config(docker_container, backup_path)
                self.app.notify_manager.send_success("GitLab config: backed up successfully", True)
            except Exception as ex:
                has_errors = True
                self.app.notify_manager.send_error(f"GitLab config: {str(ex)}", True)

            try:
                self.__backup_data(docker_container, backup_path)
                self.app.notify_manager.send_success("GitLab data: backed up successfully", True)
            except Exception as ex:
                has_errors = True
                self.app.notify_manager.send_error(f"GitLab data: {str(ex)}", True)

            return has_errors

        return self.backup_service(callback)

    def __backup_config(self, container: Container, backup_path: str) -> None:
        exit_code, _ = docker.container_exec(container, "gitlab-ctl backup-etc")
        if exit_code != 0:
            raise Exception("Unable to back up Gitlab config")

        returncode, _, _ = self.app.run_command(f'docker cp "{container.id}:/etc/gitlab/config_backup/" {backup_path}')
        if returncode != 0:
            raise Exception(f"Unable to copy Gitlab config from {container.name} container to {backup_path}")

        exit_code, _ = docker.container_exec(
            container, '/bin/bash -c "rm -f /etc/gitlab/config_backup/*.tar"', user="root"
        )
        if exit_code != 0:
            self.app.log_manager.warning(f"Unable to remove GitLab config backups from {container.name} container")

    def __backup_data(self, container: Container, backup_path: str) -> None:
        exit_code, _ = docker.container_exec(container, "gitlab-backup")
        if exit_code != 0:
            raise Exception("Unable to backup Gitlab data")

        returncode, _, _ = self.app.run_command(f'docker cp "{container.id}:/var/opt/gitlab/backups/" {backup_path}')
        if returncode != 0:
            raise Exception(f"Unable to copy Gitlab data from {container.name} container to {backup_path}")

        exit_code, _ = docker.container_exec(
            container, '/bin/bash -c "rm -f /var/opt/gitlab/backups/*.tar"', user="root"
        )
        if exit_code != 0:
            self.app.log_manager.warning(f"Unable to remove GitLab data backups from {container.name} container")
