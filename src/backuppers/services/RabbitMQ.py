from docker.models.containers import Container

from src.backuppers.Backupper import Backupper, TypeBackupperConfigProperty
from src.backuppers.Docker import docker
from src.typehints import TypeConfigContainerRabbitmq


class RabbitMQ(Backupper[TypeConfigContainerRabbitmq]):
    @property
    def _type(self) -> str:
        return "rabbitmq"

    @property
    def config(self) -> TypeBackupperConfigProperty:
        return {
            "local_storage_path": self.app.config["container_types"]["rabbitmq"]["storage_path"],
            "mirror_storage_path": "rabbitmq",
        }

    @property
    def subject(self) -> str:
        return "RabbitMQ data"

    def backup(self) -> bool:
        def callback(container: TypeConfigContainerRabbitmq, docker_container: Container, backup_path: str) -> bool:
            has_errors = False

            volume = docker.client.api.inspect_volume(container["config"]["volume"])

            docker_container.stop()

            self.app.notify_manager.send_info(f"Stopped {container['name']} container", True)

            docker.backup_volume(
                f"{self.app.backup_prefix}_{container['name']}_{container['config']['volume']}",
                volume["Mountpoint"],
                backup_path,
            )

            self.app.notify_manager.send_success(
                f"{container['name']}/{container['config']['volume']}: backed up successfully", True
            )

            docker_container.start()

            self.app.notify_manager.send_info(f"Started {container['name']} container", True)

            return not has_errors

        return self.backup_service(callback)
