from typing import List

from src.App import app
from src.cleaners.RSyncCleaner import RSyncCleaner


def run_rsync_cleaner(paths: List[str]) -> None:
    if not app.config["mirrors"]["rsync"]:
        app.notify_manager.send_warning("No RSync mirrors defined")
        return

    for rsync_mirror in app.config["mirrors"]["rsync"]:
        cleaner = RSyncCleaner(app, rsync_mirror)

        app.notify_manager.send_cleanup(
            f"Started cleaning at {app.get_current_datetime()} on {rsync_mirror['host']} RSync mirror"
        )

        for path in paths:
            cleaner.add_path(f"{rsync_mirror['storage_path']}/{path}")

        cleaner.run()

        app.notify_manager.send_cleanup(
            f"Finished cleaning at {app.get_current_datetime()} on {rsync_mirror['host']} RSync mirror"
        )
