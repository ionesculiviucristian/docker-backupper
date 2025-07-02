import click

from src.commands import backup, clear_mattermost_messages
from src.commands import ftp_backup as ftp_backup_command
from src.commands import gitlab, minio, mongo, mount, mysql, postgres, rabbitmq
from src.commands import rsync_backup as rsync_backup_command
from src.commands import run_ftp_cleaner as run_ftp_cleaner_command
from src.commands import run_local_cleaner as run_local_cleaner_command
from src.commands import run_rsync_cleaner as run_rsync_cleaner_command


@click.group()
def cli() -> None:
    pass


@click.command()
def ftp_backup() -> None:
    ftp_backup_command()


@click.command()
def run_ftp_cleaner() -> None:
    run_ftp_cleaner_command([])


@click.command()
def run_local_cleaner() -> None:
    run_local_cleaner_command([])


@click.command()
def run_rsync_cleaner() -> None:
    run_rsync_cleaner_command([])


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

# Services backup
cli.add_command(gitlab)
cli.add_command(minio)
cli.add_command(rabbitmq)

# Mounts backup
cli.add_command(mount)

# Backup cleaners
cli.add_command(run_local_cleaner)
cli.add_command(run_ftp_cleaner)
cli.add_command(run_rsync_cleaner)

# Notifiers
cli.add_command(clear_mattermost_messages)


if __name__ == "__main__":
    cli()
