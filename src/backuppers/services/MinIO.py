import re
from typing import List

from docker.models.containers import Container

from src.backuppers.Backupper import Backupper, TypeBackupperConfigProperty
from src.backuppers.Docker import docker
from src.typehints import TypeConfigContainerMinio


class MinIO(Backupper[TypeConfigContainerMinio]):
    @property
    def _type(self) -> str:
        return "minio"

    @property
    def config(self) -> TypeBackupperConfigProperty:
        return {
            "local_storage_path": self.app.config["container_types"]["minio"]["storage_path"],
            "mirror_storage_path": "minio",
        }

    @property
    def subject(self) -> str:
        return "MiniIO buckets"

    def backup(self) -> bool:
        def callback(container: TypeConfigContainerMinio, docker_container: Container, backup_path: str) -> bool:
            has_errors = False

            buckets = self.__get_container_buckets(container, docker_container)
            buckets_count = len(buckets)

            if buckets_count == 0:
                self.app.notify_manager.send_warning(f"No buckets found in {container['name']} container", True)
                return True

            self.app.notify_manager.send_info(f"Found {buckets_count} buckets in {container['name']} container", True)

            for bucket in buckets:
                try:
                    self.__export_container_bucket(container, docker_container, bucket, backup_path)
                    self.app.notify_manager.send_success(f"{bucket}: backed up successfully", True)
                except Exception as ex:
                    has_errors = True
                    self.app.notify_manager.send_error(f"{bucket}: {self.app.get_exception_trace(ex)}", True)

            return has_errors

        return self.backup_service(callback)

    def __export_container_bucket(
        self, container: TypeConfigContainerMinio, docker_container: Container, bucket: str, path: str
    ) -> None:
        backup_file = f"{self.app.backup_prefix}_{container['name']}_{bucket}.tar.gz"
        container_backup_file_path = f"/tmp/localminio_{bucket}"

        command = f"""
        bash -c '
            mc alias set localminio "{container['config']['url']}" "{container['config']['access_key']}" "{container['config']['secret_key']}" > /dev/null;
            mc mirror --quiet localminio/{bucket} {container_backup_file_path};
        '
        """  # noqa

        exit_code, _ = docker.container_exec(docker_container, command, redactor=MinIO.__redact_command)
        if exit_code != 0:
            raise Exception(f"Unable to dump {bucket} bucket from {container['name']} container")

        returncode, _, _ = self.app.run_command(f"docker cp {docker_container.id}:{container_backup_file_path} {path}")
        if returncode != 0:
            raise Exception(
                f"Unable to copy {container_backup_file_path} bucket from {container['name']} container to {path}"
            )

        exit_code, _ = docker.container_exec(docker_container, f'rm -rf "{container_backup_file_path}"')
        if exit_code != 0:
            self.app.log_manager.warning(
                f"Unable to remove {container_backup_file_path} file from {container['name']} container"
            )

        returncode, _, _ = self.app.run_command(f"tar -czf {path}/{backup_file} -C {path}/localminio_{bucket} .")
        if returncode != 0:
            raise Exception(f"Unable to create {path}/{backup_file} file")

        returncode, _, _ = self.app.run_command(f"rm -rf {path}/localminio_{bucket}")
        if returncode != 0:
            self.app.log_manager.warning(f"Unable to remove {path}/localminio_{bucket} folder")

    def __get_container_buckets(self, container: TypeConfigContainerMinio, docker_container: Container) -> List[str]:
        command = f"""
        bash -c '
            mc alias set localminio "{container['config']['url']}" "{container['config']['access_key']}" "{container['config']['secret_key']}" > /dev/null;
            mc ls localminio | while read -r line; do \
                bucket="${{line##* }}"; \
                bucket="${{bucket%/}}"; \
                echo "$bucket"; \
            done
        '
        """  # noqa

        exit_code, output = docker.container_exec(docker_container, command, redactor=MinIO.__redact_command)
        if exit_code != 0:
            raise Exception("Unable to list buckets")

        buckets: List[str] = output.split("\n")

        return [b for b in (bucket.strip() for bucket in buckets) if b]

    @staticmethod
    def __redact_command(command: str) -> str:
        return re.sub(r"(mc alias set localminio [^\s]+ )([^\s]+) ([^\s]+)", r"\1**** ****", command)
