from functools import lru_cache
from pathlib import Path

import lancedb
from lancedb.db import AsyncConnection

from api.settings import get_settings


class VectorDatabase:
    def __init__(self, uri: str) -> None:
        self._uri = uri
        self._connection: AsyncConnection | None = None

    async def connect(self) -> AsyncConnection:
        if self._connection is None or not self._connection.is_open():
            uri = Path(self._uri) if _is_local_uri(self._uri) else self._uri
            self._connection = await lancedb.connect_async(uri)

        return self._connection

    def close(self) -> None:
        if self._connection is None:
            return

        self._connection.close()
        self._connection = None


def _is_local_uri(uri: str) -> bool:
    return "://" not in uri


@lru_cache
def get_vector_db() -> VectorDatabase:
    return VectorDatabase(uri=get_settings().vector.uri)
