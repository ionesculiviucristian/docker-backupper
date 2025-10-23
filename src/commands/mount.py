import click

from src.App import app
from src.backuppers.Backupper import Backupper
from src.backuppers.mounts.Bind import Bind
from src.backuppers.mounts.Volume import Volume
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
def mount(
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
            run_local_cleaner([Bind(app).config["local_storage_path"]])
        if ftp_clean_only:
            run_ftp_cleaner([Bind(app).config["mirror_storage_path"]])
        if rsync_clean_only:
            run_rsync_cleaner([Bind(app).config["mirror_storage_path"]])
        return

    return Backupper[None].run_backupper(app, ftp_only, ftp, rsync_only, rsync, [Bind(app), Volume(app)])
