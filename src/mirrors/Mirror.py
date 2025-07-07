from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar

from src.App import App

TypeConfigMirror = TypeVar("TypeConfigMirror")


class Mirror(ABC, Generic[TypeConfigMirror]):
    app: App
    config: TypeConfigMirror

    def __init__(self, app: App, config: TypeConfigMirror):
        self.app = app
        self.config = config

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
