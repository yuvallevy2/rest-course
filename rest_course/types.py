from enum import Enum

from pydantic import PositiveInt
from pydantic.dataclasses import dataclass
from packaging import version


class UID(PositiveInt):
    pass


class BDBType(str, Enum):
    REDIS = "redis"
    MEMCACHED = "memcached"

class BDBVersion(str, Enum):
    V5 = "5.0.0"
    V6 = "6.0.0"


@dataclass
class BDB:
    uid: UID
    name: str
    memory_size: PositiveInt
    type: BDBType
    version: BDBVersion
