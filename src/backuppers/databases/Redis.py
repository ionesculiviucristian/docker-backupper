from src.backuppers.Backupper import Backupper, TypeBackupperConfigProperty
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
        return "Redis databases"

    def backup(self) -> bool:
        return True
