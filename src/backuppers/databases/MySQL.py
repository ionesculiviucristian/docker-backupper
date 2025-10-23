import re
from typing import List

from docker.models.containers import Container

from src.backuppers.Backupper import Backupper, TypeBackupperConfigProperty
from src.backuppers.Docker import docker
from src.typehints import TypeConfigContainerMysql


class MySQL(Backupper[TypeConfigContainerMysql]):
    @property
    def _type(self) -> str:
        return "mysql"

    @property
    def config(self) -> TypeBackupperConfigProperty:
        return {
            "local_storage_path": self.app.config["container_types"]["mysql"]["storage_path"],
            "mirror_storage_path": "mysql",
        }

    @property
    def subject(self) -> str:
        return "MySQL databases"

    def backup(self) -> bool:
        def callback(container: TypeConfigContainerMysql, docker_container: Container, backup_path: str) -> bool:
            has_errors = False

            databases = self.__get_container_databases(container, docker_container)
            databases_count = len(databases)

            if databases_count == 0:
                self.app.notify_manager.send_warning(f"No databases found in {container['name']} container", True)
                return False

            self.app.notify_manager.send_info(
                f"Found {databases_count} databases in {container['name']} container", True
            )

            for database in databases:
                try:
                    self.__export_container_database(container, docker_container, database, backup_path)
                    self.app.notify_manager.send_success(f"{database}: backed up successfully", True)
                except Exception as ex:
                    has_errors = True
                    self.app.notify_manager.send_error(f"{database}: {self.app.get_exception_trace(ex)}", True)

            return has_errors

        return self.backup_service(callback)

    def __export_container_database(
        self, container: TypeConfigContainerMysql, docker_container: Container, database: str, path: str
    ) -> None:
        backup_file = f"{self.app.backup_prefix}_{container['name']}_{database}.sql.gz"
        container_backup_file_path = f"/tmp/{backup_file}"

        command = f"""
        bash -c '
            set -euo pipefail;
            rm -f "{container_backup_file_path}";
            echo -e "[mysqldump]\nuser={container['config']['username']}\npassword={container['config']['password']}" \
            | mysqldump \
                --defaults-extra-file=/dev/stdin \
                --no-create-db \
                --skip-comments \
                --add-drop-table \
                --skip-add-locks \
                --routines \
                --triggers \
                --dump-date \
                --quote-names \
                "{database}" \
            | gzip > "{container_backup_file_path}"
        '
        """  # noqa

        exit_code, _ = docker.container_exec(docker_container, command, redactor=MySQL.__redact_command)
        if exit_code != 0:
            raise Exception(f"Unable to dump {database} database from {container['name']} container")

        returncode, _, _ = self.app.run_command(
            f'docker cp "{docker_container.id}:{container_backup_file_path}" {path}'
        )
        if returncode != 0:
            raise Exception(f"Unable to copy {database} database from {container['name']} container to {path}")

        exit_code, _ = docker.container_exec(docker_container, f'rm -f "{container_backup_file_path}"')
        if exit_code != 0:
            self.app.log_manager.warning(
                f"Unable to remove {container_backup_file_path} file from {container['name']} container"
            )

    def __get_container_databases(self, container: TypeConfigContainerMysql, docker_container: Container) -> List[str]:
        command = f"""
        bash -c '
            set -euo pipefail;
            echo -e "[client]\nuser={container['config']['username']}\npassword={container['config']['password']}" \
            | mysql \
                --defaults-extra-file=/dev/stdin \
                -e "show databases" \
                -s --skip-column-names
        '
        """  # noqa

        exit_code, output = docker.container_exec(docker_container, command, redactor=MySQL.__redact_command)
        if exit_code != 0:
            raise Exception("Unable to list databases")

        databases: List[str] = output.split("\n")

        return [
            database.strip()
            for database in databases
            if database and database.strip() not in ("information_schema", "performance_schema", "mysql", "sys", "test")
        ]

    @staticmethod
    def __redact_command(command: str) -> str:
        return re.sub(r"] user=[^\s]+ password=[^\s]+", r"] user=**** password=****", command)
