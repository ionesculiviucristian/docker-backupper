from typing import Generic, List, Literal, TypedDict, TypeVar, Union


class TypeConfigNotifierEmailSMTP(TypedDict):
    host: str
    username: str
    password: str
    port: int


class TypeConfigNotifierEmail(TypedDict):
    active: bool
    from_: str
    recipients: List[str]
    smtp: TypeConfigNotifierEmailSMTP


class TypeConfigNotifierMattermost(TypedDict):
    active: bool
    api_url: str
    channel: str
    retention_days: int
    token: str


class TypeConfigNotifiers(TypedDict):
    email: TypeConfigNotifierEmail
    mattermost: TypeConfigNotifierMattermost


class TypeConfigMountBindContainerPath(TypedDict):
    name: str
    path: str


class TypeConfigMountBindContainer(TypedDict):
    name: str
    paths: List[TypeConfigMountBindContainerPath]


class TypeConfigMountBind(TypedDict):
    containers: List[TypeConfigMountBindContainer]


class TypeConfigMounts(TypedDict):
    binds: TypeConfigMountBind
    storage_path: str
    volumes: List[str]


class TypeConfigMirrorFTPConfig(TypedDict):
    username: str
    password: str
    port: int


class TypeConfigMirrorFTP(TypedDict):
    host: str
    config: TypeConfigMirrorFTPConfig
    retention_days: int
    storage_path: str


class TypeConfigMirrorRSyncConfig(TypedDict):
    username: str


class TypeConfigMirrorRSync(TypedDict):
    host: str
    config: TypeConfigMirrorRSyncConfig
    retention_days: int
    storage_path: str


class TypeConfigMirrors(TypedDict):
    ftp: List[TypeConfigMirrorFTP]
    rsync: List[TypeConfigMirrorRSync]


class TypeConfigLogs(TypedDict):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    path: str


GenericConfigContainerType = TypeVar("GenericConfigContainerType", bound=str)
GenericConfigContainerConfig = TypeVar("GenericConfigContainerConfig")


class TypeConfigContainerGeneric(TypedDict, Generic[GenericConfigContainerType, GenericConfigContainerConfig]):
    name: str
    type: GenericConfigContainerType
    config: GenericConfigContainerConfig


class TypeConfigContainerRedisConfig(TypedDict):
    password: str


class TypeConfigContainerRabbitmqConfig(TypedDict):
    volume: str


class TypeConfigContainerPostgresConfig(TypedDict):
    username: str
    password: str


class TypeConfigContainerMysqlConfig(TypedDict):
    username: str
    password: str


class TypeConfigContainerMongoConfig(TypedDict):
    username: str
    password: str


class TypeConfigContainerMinioConfig(TypedDict):
    access_key: str
    secret_key: str
    url: str


class TypeConfigContainerGitlabConfig(TypedDict):
    pass


TypeConfigContainerGitlab = TypeConfigContainerGeneric[Literal["gitlab"], TypeConfigContainerGitlabConfig]
TypeConfigContainerMinio = TypeConfigContainerGeneric[Literal["minio"], TypeConfigContainerMinioConfig]
TypeConfigContainerMongo = TypeConfigContainerGeneric[Literal["mongo"], TypeConfigContainerMongoConfig]
TypeConfigContainerMysql = TypeConfigContainerGeneric[Literal["mysql"], TypeConfigContainerMysqlConfig]
TypeConfigContainerPostgres = TypeConfigContainerGeneric[Literal["postgres"], TypeConfigContainerPostgresConfig]
TypeConfigContainerRabbitmq = TypeConfigContainerGeneric[Literal["rabbitmq"], TypeConfigContainerRabbitmqConfig]
TypeConfigContainerRedis = TypeConfigContainerGeneric[Literal["redis"], TypeConfigContainerRedisConfig]

TypeConfigContainers = Union[
    None,
    TypeConfigContainerGitlab,
    TypeConfigContainerMinio,
    TypeConfigContainerMongo,
    TypeConfigContainerMysql,
    TypeConfigContainerPostgres,
    TypeConfigContainerRabbitmq,
    TypeConfigContainerRedis,
]


class TypeConfigContainerType(TypedDict):
    storage_path: str


class TypeConfigContainerTypes(TypedDict):
    gitlab: TypeConfigContainerType
    minio: TypeConfigContainerType
    mongo: TypeConfigContainerType
    mysql: TypeConfigContainerType
    postgres: TypeConfigContainerType
    rabbitmq: TypeConfigContainerType
    redis: TypeConfigContainerType


class TypeConfig(TypedDict):
    retention_days: int
    containers: List[TypeConfigContainers]
    container_types: TypeConfigContainerTypes
    logs: TypeConfigLogs
    mirrors: TypeConfigMirrors
    mounts: TypeConfigMounts
    notifiers: TypeConfigNotifiers
