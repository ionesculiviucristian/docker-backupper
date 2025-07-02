from typing import List

from src.App import app
from src.cleaners.FTPCleaner import FTPCleaner


def run_ftp_cleaner(paths: List[str]) -> None:
    if not app.config["mirrors"]["ftp"]:
        app.notify_manager.send_warning("No FTP mirrors defined")
        return

    for ftp_mirror in app.config["mirrors"]["ftp"]:
        cleaner = FTPCleaner(app, ftp_mirror)

        app.notify_manager.send_cleanup(
            f"Started cleaning at {app.get_current_datetime()} on {ftp_mirror['host']} FTP mirror"
        )

        for path in paths:
            cleaner.add_path(f"{ftp_mirror['storage_path']}/{path}")

        cleaner.run()

        app.notify_manager.send_cleanup(
            f"Finished cleaning at {app.get_current_datetime()} on {ftp_mirror['host']} FTP mirror"
        )
