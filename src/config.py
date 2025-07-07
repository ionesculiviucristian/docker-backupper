from os import path
from typing import cast

from yaml import load

try:
    from yaml import CLoader

    Loader = cast(type, CLoader)
except ImportError:
    from yaml import Loader

from src.paths import YAML_FILE_PATH
from src.typehints import TypeConfig


def merge_configs(default: TypeConfig, override: TypeConfig) -> TypeConfig:
    result = default.copy()
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge_configs(result[key], value)  # type: ignore
        elif value is None:
            result[key] = result.get(key)  # type: ignore
        else:
            result[key] = value  # type: ignore
    return result


default_config: TypeConfig = {
    "retention_days": 7,
    "container_types": {
        "gitlab": {"storage_path": ""},
        "minio": {"storage_path": ""},
        "mongo": {"storage_path": ""},
        "mysql": {"storage_path": ""},
        "postgres": {"storage_path": ""},
        "rabbitmq": {"storage_path": ""},
    },
    "containers": [],
    "logs": {"level": "DEBUG", "path": "/tmp"},
    "mirrors": {"ftp": [], "rsync": []},
    "mounts": {"binds": {"containers": []}, "storage_path": "", "volumes": []},
    "notifiers": {
        "email": {
            "active": False,
            "from_": "",
            "recipients": [],
            "smtp": {"host": "", "password": "", "port": 465, "username": ""},
        },
        "mattermost": {
            "active": False,
            "api_url": "",
            "channel": "",
            "retention_days": 3,
            "token": "",
        },
    },
}

if not path.exists(YAML_FILE_PATH):
    print(f"{YAML_FILE_PATH} not found, using default config!")
    config = default_config
else:
    with open(YAML_FILE_PATH) as stream:
        file_config: TypeConfig = load(stream, Loader=Loader)
        config = merge_configs(default_config, file_config)
