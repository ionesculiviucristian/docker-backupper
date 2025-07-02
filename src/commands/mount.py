import click

from src.App import app
from src.backuppers.Backupper import Backupper
from src.backuppers.mounts.Bind import Bind
from src.backuppers.mounts.Volume import Volume


@click.command()
@click.option("--ftp", is_flag=True)
@click.option("--ftp-only", is_flag=True)
@click.option("--rsync", is_flag=True)
@click.option("--rsync-only", is_flag=True)
def mount(ftp: bool, ftp_only: bool, rsync: bool, rsync_only: bool) -> None:
    return Backupper[None].run_backupper(app, ftp, ftp_only, rsync, rsync_only, [Bind(app), Volume(app)])
