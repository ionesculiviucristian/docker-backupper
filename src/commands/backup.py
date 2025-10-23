from typing import Any, List, Type

import click

from src.App import app
from src.backuppers.Backupper import Backupper
from src.backuppers.databases import Mongo, MySQL, Postgres, Redis
from src.backuppers.mounts import Bind, Volume
from src.backuppers.services import GitLab, MinIO, RabbitMQ
from src.commands.ftp_backup import ftp_backup
from src.commands.rsync_backup import rsync_backup
from src.commands.run_ftp_cleaner import run_ftp_cleaner
from src.commands.run_local_cleaner import run_local_cleaner
from src.commands.run_rsync_cleaner import run_rsync_cleaner


@click.command()
@click.option("--clean-only", is_flag=True)
@click.option("--ftp-clean-only", is_flag=True)
@click.option("--ftp-only", is_flag=True)
@click.option("--ftp", is_flag=True)
@click.option("--rsync-clean-only", is_flag=True)
@click.option("--rsync-only", is_flag=True)
@click.option("--rsync", is_flag=True)
def backup(
    clean_only: bool,
    ftp_clean_only: bool,
    ftp_only: bool,
    ftp: bool,
    rsync_clean_only: bool,
    rsync_only: bool,
    rsync: bool,
) -> None:
    try:
        backuppers: List[Type[Backupper[Any]]] = [Bind, Volume, GitLab, MinIO, Mongo, MySQL, Postgres, RabbitMQ, Redis]

        cleaner_paths: List[str] = []

        app.notify_manager.send_time(
            f"Started backup at {app.get_current_datetime()} on {app.hostname} {app.external_ip}"
        )

        if clean_only:
            for backupper in backuppers:
                backupper_instance = backupper(app)
                cleaner_paths.append(backupper_instance.config["local_storage_path"])

            return run_local_cleaner(cleaner_paths)

        if ftp_clean_only:
            for backupper in backuppers:
                backupper_instance = backupper(app)
                cleaner_paths.append(backupper_instance.config["mirror_storage_path"])

            return run_ftp_cleaner(cleaner_paths)

        if rsync_clean_only:
            for backupper in backuppers:
                backupper_instance = backupper(app)
                cleaner_paths.append(backupper_instance.config["mirror_storage_path"])

            return run_rsync_cleaner(cleaner_paths)

        if not ftp_only and not rsync_only:
            for backupper in backuppers:
                backupper_instance = backupper(app)
                if backupper_instance.is_backup_disabled():
                    app.notify_manager.send_warning(f"Backing up {backupper_instance.subject} is disabled")
                    continue
                if backupper_instance.backup():
                    cleaner_paths.append(backupper_instance.config["local_storage_path"])

        if ftp or ftp_only:
            ftp_cleaner_paths = ftp_backup()
            run_ftp_cleaner(ftp_cleaner_paths)

        if rsync or rsync_only:
            rsync_cleaner_paths = rsync_backup()
            run_rsync_cleaner(rsync_cleaner_paths)

        if not ftp_only and not rsync_only:
            run_local_cleaner(cleaner_paths)

        app.notify_manager.send_time(f"Finished backup at {app.get_current_datetime()}")
    except Exception as ex:
        app.notify_manager.send_error(app.get_exception_trace(ex))
    finally:
        app.notify_manager.send_log_file()
