import click

from src.App import app
from src.backuppers.Backupper import Backupper
from src.backuppers.databases.Mongo import Mongo
from src.typehints import TypeConfigContainerMongo


@click.command()
@click.option("--ftp", is_flag=True)
@click.option("--ftp-only", is_flag=True)
@click.option("--rsync", is_flag=True)
@click.option("--rsync-only", is_flag=True)
def mongo(ftp: bool, ftp_only: bool, rsync: bool, rsync_only: bool) -> None:
    return Backupper[TypeConfigContainerMongo].run_backupper(app, ftp, ftp_only, rsync, rsync_only, Mongo(app))
