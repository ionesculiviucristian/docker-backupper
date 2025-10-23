from typing import cast

import click

from src.App import app
from src.backuppers.Docker import (
    TypeDockerContainersPruneResult,
    TypeDockerImagesPruneResult,
    TypeDockerNetworksPruneResult,
    TypeDockerVolumesPruneResult,
    docker,
)


@click.command()
def prune() -> None:
    try:
        app.notify_manager.send_time(
            f"Started pruning docker at {app.get_current_datetime()} from {app.hostname} {app.external_ip}"  # noqa
        )

        app.notify_manager.send_action("Pruning containers")
        result = cast(TypeDockerContainersPruneResult, docker.client.containers.prune())  # type: ignore
        app.log_manager.debug(str(result))

        app.notify_manager.send_action("Pruning images")
        result = cast(TypeDockerImagesPruneResult, docker.client.images.prune(filters={"dangling": False}))  # type: ignore # noqa
        app.log_manager.debug(str(result))

        app.notify_manager.send_action("Pruning networks")
        result = cast(TypeDockerNetworksPruneResult, docker.client.networks.prune())  # type: ignore
        app.log_manager.debug(str(result))

        app.notify_manager.send_action("Pruning volumes")
        result = cast(TypeDockerVolumesPruneResult, docker.client.volumes.prune())  # type: ignore
        app.log_manager.debug(str(result))

        app.notify_manager.send_time(f"Finished pruning docker at {app.get_current_datetime()}")
    except Exception as ex:
        app.notify_manager.send_error(app.get_exception_trace(ex))
    finally:
        app.notify_manager.send_log_file()
