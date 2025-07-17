import click

from src.App import app


@click.command()
def clear_mattermost_messages() -> None:
    try:
        app.notify_manager.send_time(
            f"Started clearing Mattermost messages at {app.get_current_datetime()} from {app.hostname} {app.external_ip}"  # noqa
        )
        result = app.notify_manager.mattermost.clear_messages()
        if result is None:
            app.notify_manager.send_error("Failed to clear messages")
        else:
            app.notify_manager.send_info(f"Deleted {result['succeeded']} and failed {result['failed']}")

        app.notify_manager.send_time(f"Finished clearing at {app.get_current_datetime()}")
    except Exception as ex:
        app.notify_manager.send_error(app.get_exception_trace(ex))
    finally:
        app.notify_manager.send_log_file()
