import click

from src.App import app
from src.backuppers.Backupper import Backupper
from src.backuppers.services.GitLab import GitLab
from src.typehints import TypeConfigContainerGitlab


@click.command()
@click.option("--ftp", is_flag=True)
@click.option("--ftp-only", is_flag=True)
@click.option("--rsync", is_flag=True)
@click.option("--rsync-only", is_flag=True)
def gitlab(ftp: bool, ftp_only: bool, rsync: bool, rsync_only: bool) -> None:
    return Backupper[TypeConfigContainerGitlab].run_backupper(app, ftp, ftp_only, rsync, rsync_only, GitLab(app))
