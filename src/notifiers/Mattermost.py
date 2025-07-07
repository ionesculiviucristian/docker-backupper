import json
import time
from typing import Any, List, Mapping

import requests

from src.loggers.LogManager import LogManager
from src.notifiers.Notifier import Notifier, TypeContructorHelpersParam
from src.typehints import TypeConfigNotifierMattermost


class Mattermost(Notifier[TypeConfigNotifierMattermost]):
    deletable_posts: List[str]

    def __init__(
        self, config: TypeConfigNotifierMattermost, log_manager: LogManager, helpers: TypeContructorHelpersParam
    ):
        super().__init__(config, log_manager, helpers)
        self.deletable_posts = []

    def clear_messages(self) -> bool:
        try:
            page = 1
            while True:
                self.log_manager.info(f"Deleting posts from page {page}")

                posts = self.__get_posts(page, 100)

                if not posts:
                    break

                for post_id, post in posts.items():
                    if self.__is_post_deletable(post["create_at"]):
                        self.deletable_posts.append(post_id)
                page += 1

            for deletable_post in self.deletable_posts:
                response = requests.delete(
                    f"{self.config['api_url']}/posts/{deletable_post}",
                    headers=self.__get_headers(),
                )
                if response.status_code != 200:
                    self.log_manager.warning(f"Failed to delete post {deletable_post}: {response.text}")
                else:
                    self.log_manager.debug(f"Deleted post {deletable_post}")

            return True
        except Exception as e:
            self.log_manager.error(f"Unable to get posts: {str(e)}")
            return False

    def send_log_file(self, path: str) -> bool:
        try:
            data = {"channel_id": self.config["channel"]}

            headers = {
                "Authorization": f"Bearer {self.config['token']}",
            }

            with open(path, "rb") as stream:
                files = {"files": ("report.txt", stream)}

                response = requests.post(
                    f"{self.config['api_url']}/files",
                    headers=headers,
                    files=files,
                    data=data,
                )
                response.raise_for_status()

                file_info = response.json()
                file_id = file_info["file_infos"][0]["id"]

                payload: dict[str, str | list[str]] = {
                    "channel_id": self.config["channel"],
                    "file_ids": [file_id],
                }

                response = requests.post(f"{self.config['api_url']}/posts", headers=headers, json=payload)
                response.raise_for_status()
                return True
        except Exception as e:
            self.log_manager.error(f"Unable to upload {path}: {str(e)}")
            return False

    def send_message(self, message: str) -> bool:
        try:
            payload = {
                "channel_id": self.config["channel"],
                "message": message,
            }

            response = requests.post(
                f"{self.config['api_url']}/posts",
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
            "Authorization": f"Bearer {self.config['token']}",
            "Content-Type": "application/json",
        }

    def __get_posts(self, page: int = 0, per_page: int = 100) -> Any:
        response = requests.get(
            f"{self.config['api_url']}/channels/{self.config['channel']}/posts?page={page}&per_page={per_page}",  # noqa
            headers=self.__get_headers(),
        )
        response.raise_for_status()

        return response.json().get("posts", {})

    def __is_post_deletable(self, created_at: int) -> bool:
        now = int(time.time() * 1000)
        post_age = (now - created_at) / 24 * 60 * 60 * 1000
        return post_age > self.config["retention_days"]
