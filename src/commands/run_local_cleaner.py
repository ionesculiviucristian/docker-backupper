from typing import List

from src.App import app
from src.cleaners.LocalCleaner import LocalCleaner


def run_local_cleaner(paths: List[str]) -> None:
    app.notify_manager.send_time(
        f"Started local cleaning at {app.get_current_datetime()} on {app.hostname} {app.external_ip}"
    )

    cleaner = LocalCleaner(app, app.config)

    for path in paths:
        cleaner.add_path(path)

    cleaner.run()

    app.notify_manager.send_time(
        f"Finished local cleaning at {app.get_current_datetime()} on {app.hostname} {app.external_ip}"
    )
