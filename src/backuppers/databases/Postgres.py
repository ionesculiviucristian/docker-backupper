import re
from typing import List

from docker.models.containers import Container

from src.backuppers.Backupper import Backupper, TypeBackupperConfigProperty
from src.backuppers.Docker import docker
from src.typehints import TypeConfigContainerPostgres


class Postgres(Backupper[TypeConfigContainerPostgres]):
    @property
    def _type(self) -> str:
        return "postgres"

    @property
    def config(self) -> TypeBackupperConfigProperty:
        return {
            "local_storage_path": self.app.config["container_types"]["postgres"]["storage_path"],
            "mirror_storage_path": "postgres",
        }

    @property
    def subject(self) -> str:
        return "Postgres databases"

    def backup(self) -> bool:
        def callback(container: TypeConfigContainerPostgres, docker_container: Container, backup_path: str) -> bool:
            has_errors = False

            databases = self.__get_container_databases(container, docker_container)
            databases_count = len(databases)

            if databases_count == 0:
                self.app.notify_manager.send_warning(f"No databases found in {container['name']} container", True)
                return True

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
        self, container: TypeConfigContainerPostgres, docker_container: Container, database: str, path: str
    ) -> None:
        backup_file = f"{self.app.backup_prefix}_{container['name']}_{database}.sql.gz"
        container_backup_file_path = f"/tmp/{backup_file}"

        command = f"""
        bash -c '
            set -euo pipefail;
            rm -f "{container_backup_file_path}";
            PGPASSWORD="{container['config']['password']}" \
            pg_dump -U "{container['config']['username']}" \
                --no-owner \
                --no-privileges \
                --clean \
                --if-exists \
                --quote-all-identifiers \
                --dbname="{database}" \
            | gzip > "{container_backup_file_path}"
        '
        """

        exit_code, output = docker.container_exec(docker_container, command, redactor=Postgres.__redact_command)

        if exit_code != 0:
            raise Exception(f"Unable to dump {database} database from {container['name']} container: {output}")

        returncode, _, _ = self.app.run_command(
            f'docker cp "{docker_container.id}:{container_backup_file_path}" {path}'
        )
        if returncode != 0:
            raise Exception(f"Unable to copy {database} database from {container['name']} container to {path}")

        exit_code, output = docker.container_exec(docker_container, f'rm -f "{container_backup_file_path}"')
        if exit_code != 0:
            self.app.log_manager.warning(
                f"Unable to remove {container_backup_file_path} file from {container['name']} container"
            )

    def __get_container_databases(
        self, container: TypeConfigContainerPostgres, docker_container: Container
    ) -> List[str]:
        command = f"""
        sh -c '
            PGPASSWORD="{container['config']['password']}" \
            psql -U "{container['config']['username']}" -d postgres -t -c "SELECT datname FROM pg_database WHERE datistemplate = false;"
        '
        """  # noqa

        exit_code, output = docker.container_exec(docker_container, command, redactor=Postgres.__redact_command)
        if exit_code != 0:
            raise Exception("Unable to list databases")

        databases: List[str] = output.split("\n")

        return [database.strip() for database in databases if database and database.strip() not in ("postgres", "test")]

    @staticmethod
    def __redact_command(command: str) -> str:
        command = re.sub(r"(PGPASSWORD=)[^\s]+", r"\1****", command)
        command = re.sub(r"(pg_dump -U )[^\s]+", r"\1****", command)
        return re.sub(r"(psql -U )[^\s]+", r"\1****", command)
