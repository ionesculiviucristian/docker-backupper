import re
from typing import Callable, Dict, List, Literal, Optional, Tuple, TypedDict, cast

import docker as docker_lib
from docker import DockerClient
from docker.models.containers import Container
from docker.types.services import Mount

from src.App import app


class TypeDockerContainersPruneResult(TypedDict):
    ContainersDeleted: List[str] | None
    SpaceReclaimed: int


class TypeDockerImagesPruneResult(TypedDict):
    ImagesDeleted: List[Dict[Literal["Deleted"] | Literal["Untagged"], str]] | None
    SpaceReclaimed: int


class TypeDockerNetworksPruneResult(TypedDict):
    NetworksDeleted: List[str] | None


class TypeDockerVolumesPruneResult(TypedDict):
    VolumesDeleted: List[str]
    SpaceReclaimed: int


class Docker:
    client: DockerClient

    def __init__(self) -> None:
        self.client = docker_lib.from_env()

    def find_volume(self, volume: str) -> Tuple[Mount, Container] | None:
        containers = docker.get_containers_list()

        for container in containers:
            for mount in self.get_container_mounts(container):
                if mount["Type"] == "volume" and mount["Name"] == volume:
                    return mount, container

        return None

    @staticmethod
    def backup_volume(
        filename: str,
        from_source: str,
        to_source: str,
    ) -> bytes:
        command = f"sh -c 'tar -czf /backup/{filename}.tar.gz /data'"

        app.log_manager.debug(f"Running {command} inside temporary container")

        return docker.client.containers.run(
            "alpine",
            remove=True,
            working_dir="/",
            command=command,
            mounts=[
                Mount(
                    type="bind",
                    source=from_source,
                    target="/data",
                ),
                Mount(
                    type="bind",
                    source=to_source,
                    target="/backup",
                ),
            ],
        )

    @staticmethod
    def container_exec(
        container: Container, command: str, user: str = "", redactor: Optional[Callable[[str], str]] = None
    ) -> Tuple[int, str]:
        exit_code, output = container.exec_run(command, user=user)  # type: ignore

        exit_code = cast(int, exit_code)
        output = cast(bytes, output)
        output = output.decode("utf-8", errors="ignore").strip()

        command = re.sub(r"\s+", " ", command).strip()
        command = redactor(command) if redactor else command

        app.log_manager.debug(
            f"Executing `{command}` in {container.name} as user `{user}` returned {exit_code} and outputted {output}"
        )

        return exit_code, output

    @staticmethod
    def find_container(container: str) -> Container | None:
        for docker_container in docker.get_containers_list():
            if docker_container.name == container:
                return docker_container

        return None

    @staticmethod
    def get_containers_list() -> List[Container]:
        containers = docker.client.containers.list()  # type: ignore

        return cast(List[Container], containers)

    @staticmethod
    def get_container_mounts(container: Container) -> List[Mount]:
        container_info = docker.client.api.inspect_container(container.id)  # type: ignore

        return container_info["Mounts"] if "Mounts" in container_info else []  # type: ignore


docker = Docker()
