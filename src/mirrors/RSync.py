from typing import List

from src.App import App
from src.mirrors.Mirror import Mirror
from src.typehints import TypeConfigMirrorRSync


class RSync(Mirror[TypeConfigMirrorRSync]):
    ssh_login: str

    def __init__(self, app: App, config: TypeConfigMirrorRSync) -> None:
        super().__init__(app, config)
        self.ssh_login = f"{self.config['config']['username']}@{self.config['host']}"

    def connect(self) -> None:
        returncode, _, _ = self.app.run_command(f"ssh {self.ssh_login} 'true'")
        if returncode != 0:
            raise Exception(f"Connection to RSync mirror at {self.config['host']} failed")

        self.app.log_manager.info(f"Established connection to RSync mirror at {self.config['host']}")

    def list_items(self, path: str) -> List[str]:
        returncode, stdout, _ = self.app.run_command(f"ssh {self.ssh_login} 'ls -1 {path}'")
        if returncode != 0:
            self.app.notify_manager.send_error(f"Unable to list folders in {path} on {self.config['host']}")
            return []
        return stdout.splitlines()

    def remove_path_items(self, path: str) -> None:
        returncode, _, _ = self.app.run_command(f"ssh {self.ssh_login} 'rm -rf {path}'")
        if returncode != 0:
            self.app.notify_manager.send_error(f"Unable to remove {path} on {self.config['host']}")

    def transfer(self, source: str, destination: str) -> bool:
        destination = self.app.generate_backup_path(f"{self.config['storage_path']}/{destination}")

        returncode, _, _ = self.app.run_command(f"ssh {self.ssh_login} 'mkdir -p {destination}'")
        if returncode != 0:
            self.app.notify_manager.send_error(f"Unable to create {destination} on remote {self.config['host']}")
            return False

        returncode, _, _ = self.app.run_command(
            f"rsync -av --info=progress2 -e ssh {source} {self.ssh_login}:{destination}"
        )
        if returncode == 0:
            self.app.notify_manager.send_success(f"Transferred {source} to {destination}")
            return True
        else:
            self.app.notify_manager.send_error(f"Unable to transfer {source} to {destination}")
            return False
