from abc import ABC, abstractmethod
from typing import List

from src.App import App


class Mirror(ABC):
    app: App

    def __init__(self, app: App):
        self.app = app

    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def list_items(self, path: str) -> List[str]:
        pass

    @abstractmethod
    def remove_path_items(self, path: str) -> None:
        pass

    @abstractmethod
    def transfer(self, source: str, destination: str) -> bool:
        pass
