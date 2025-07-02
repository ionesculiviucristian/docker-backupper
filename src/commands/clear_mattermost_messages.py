import click

from src.App import app


@click.command()
def clear_mattermost_messages() -> None:
    app.notify_manager.mattermost.clear_messages()
