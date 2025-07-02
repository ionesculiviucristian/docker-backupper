import json
from typing import Any, Mapping

import requests

from src.notifiers.Notifier import Notifier


class Mattermost(Notifier):
    def clear_messages(self) -> bool:
        try:
            page = 0
            while True:
                posts = self.__get_posts(page, 100)
                if not posts:
                    break

                for post in posts:
                    response = requests.delete(
                        f"{self.config['notifiers']['mattermost']['api_url']}/posts/{post}",
                        headers=self.__get_headers(),
                    )
                    if response.status_code != 200:
                        self.log_manager.warning(f"Failed to delete post {post}: {response.text}")
                page += 1
            return True
        except Exception as e:
            self.log_manager.error(f"Unable to get posts: {str(e)}")
            return False

    def send_log_file(self, path: str) -> bool:
        try:
            data = {"channel_id": self.config["notifiers"]["mattermost"]["channel"]}

            headers = {
                "Authorization": f"Bearer {self.config['notifiers']['mattermost']['token']}",
            }

            with open(path, "rb") as stream:
                files = {"files": ("report.txt", stream)}

                response = requests.post(
                    f"{self.config['notifiers']['mattermost']['api_url']}/files",
                    headers=headers,
                    files=files,
                    data=data,
                )
                response.raise_for_status()

                file_info = response.json()
                file_id = file_info["file_infos"][0]["id"]

                payload: dict[str, str | list[str]] = {
                    "channel_id": self.config["notifiers"]["mattermost"]["channel"],
                    "file_ids": [file_id],
                }

                response = requests.post(
                    f"{self.config['notifiers']['mattermost']['api_url']}/posts", headers=headers, json=payload
                )
                response.raise_for_status()
                return True
        except Exception as e:
            self.log_manager.error(f"Unable to upload {path}: {str(e)}")
            return False

    def send_message(self, message: str) -> bool:
        try:
            payload = {
                "channel_id": self.config["notifiers"]["mattermost"]["channel"],
                "message": message,
            }

            response = requests.post(
                f"{self.config['notifiers']['mattermost']['api_url']}/posts",
                data=json.dumps(payload),
                headers=self.__get_headers(),
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.log_manager.error(f"Unable to send post: {str(e)}")
            return False

    def __get_headers(self) -> Mapping[str, str]:
        return {
            "Authorization": f"Bearer {self.config['notifiers']['mattermost']['token']}",
            "Content-Type": "application/json",
        }

    def __get_posts(self, page: int = 0, per_page: int = 100) -> Any:
        response = requests.get(
            f"{self.config['notifiers']['mattermost']['api_url']}/channels/{self.config['notifiers']['mattermost']['channel']}/posts?page={page}&per_page={per_page}",  # noqa
            headers=self.__get_headers(),
        )
        response.raise_for_status()

        return response.json().get("posts", {})
