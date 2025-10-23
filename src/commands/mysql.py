import click

from src.App import app
from src.backuppers.Backupper import Backupper
from src.backuppers.databases.MySQL import MySQL
from src.commands.run_ftp_cleaner import run_ftp_cleaner
from src.commands.run_local_cleaner import run_local_cleaner
from src.commands.run_rsync_cleaner import run_rsync_cleaner
from src.typehints import TypeConfigContainerMysql


@click.command()
@click.option("--clean-only", is_flag=True)
@click.option("--ftp-clean-only", is_flag=True)
@click.option("--ftp-only", is_flag=True)
@click.option("--ftp", is_flag=True)
@click.option("--rsync-clean-only", is_flag=True)
@click.option("--rsync-only", is_flag=True)
@click.option("--rsync", is_flag=True)
def mysql(
    clean_only: bool,
    ftp_clean_only: bool,
    ftp_only: bool,
    ftp: bool,
    rsync_clean_only: bool,
    rsync_only: bool,
    rsync: bool,
) -> None:
    if clean_only or ftp_clean_only or rsync_clean_only:
        if clean_only:
            run_local_cleaner([MySQL(app).config["local_storage_path"]])
        if ftp_clean_only:
            run_ftp_cleaner([MySQL(app).config["mirror_storage_path"]])
        if rsync_clean_only:
            run_rsync_cleaner([MySQL(app).config["mirror_storage_path"]])
        return

    return Backupper[TypeConfigContainerMysql].run_backupper(app, ftp_only, ftp, rsync_only, rsync, MySQL(app))
