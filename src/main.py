import click

from src.commands import backup, clear_mattermost_messages
from src.commands import ftp_backup as ftp_backup_command
from src.commands import (
    gitlab,
    minio,
    mongo,
    mount,
    mysql,
    postgres,
    prune,
    rabbitmq,
    redis,
)
from src.commands import rsync_backup as rsync_backup_command


@click.group()
def cli() -> None:
    pass


@click.command()
def ftp_backup() -> None:
    ftp_backup_command()


@click.command()
def rsync_backup() -> None:
    rsync_backup_command()


# Local and mirror backups
cli.add_command(backup)
cli.add_command(ftp_backup)
cli.add_command(rsync_backup)

# Databases backup
cli.add_command(mysql)
cli.add_command(postgres)
cli.add_command(mongo)
cli.add_command(redis)

# Docker
cli.add_command(prune)

# Services backup
cli.add_command(gitlab)
cli.add_command(minio)
cli.add_command(rabbitmq)

# Mounts backup
cli.add_command(mount)

# Notifiers
cli.add_command(clear_mattermost_messages)

if __name__ == "__main__":
    cli()
