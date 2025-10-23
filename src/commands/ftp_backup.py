from typing import Any, List, Set, Type

from src.App import app
from src.backuppers.Backupper import Backupper
from src.backuppers.databases.Mongo import Mongo
from src.backuppers.databases.MySQL import MySQL
from src.backuppers.databases.Postgres import Postgres
from src.backuppers.databases.Redis import Redis
from src.backuppers.mounts.Bind import Bind
from src.backuppers.mounts.Volume import Volume
from src.backuppers.services.GitLab import GitLab
from src.backuppers.services.MinIO import MinIO
from src.backuppers.services.RabbitMQ import RabbitMQ
from src.mirrors import FTP


def ftp_backup() -> List[str]:
    if not app.config["mirrors"]["ftp"]:
        app.notify_manager.send_warning("No FTP mirrors defined")
        return []

    cleanable_paths: Set[str] = set()

    backuppers: List[Type[Backupper[Any]]] = [Bind, Volume, GitLab, MinIO, Mongo, MySQL, Postgres, RabbitMQ, Redis]

    for ftp_mirror in app.config["mirrors"]["ftp"]:
        ftp_client = FTP(app, ftp_mirror)
        ftp_client.connect()

        app.notify_manager.send_connect(f"Connected to {ftp_mirror['host']}")

        for backupper in backuppers:
            backupper_instance = backupper(app)

            app.notify_manager.send_action(f"Transferring {backupper_instance.subject}")

            failed = False

            for source in app.get_backup_file_paths(backupper_instance.config["local_storage_path"]):
                if not ftp_client.transfer(source, backupper_instance.config["mirror_storage_path"]):
                    failed = True

            if not failed:
                cleanable_paths.add(backupper_instance.config["mirror_storage_path"])

        ftp_client.quit()

    return list(cleanable_paths)
