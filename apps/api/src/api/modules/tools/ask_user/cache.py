from uuid import UUID, uuid4

import pyarrow as pa
from lancedb.table import AsyncTable

from api.modules.tools.ask_user.models import AskUserCacheEntry, AskUserCacheEntryData
from api.shared.time import utc_now
from api.vector.database import VectorDatabase

ASK_USER_CACHE_TABLE = "ask_user_answer_cache"


class AskUserCacheRepository:
    def __init__(
        self,
        *,
        vector_db: VectorDatabase,
    ) -> None:
        self._vector_db = vector_db

    async def add_entry(self, data: AskUserCacheEntryData) -> AskUserCacheEntry:
        table = await self._get_table(vector_size=len(data.vector))
        entry_id = uuid4()
        await table.add(
            [
                {
                    "id": str(entry_id),
                    "session_id": str(data.session_id),
                    "vector": data.vector,
                    "source_completed_event_id": str(data.source_completed_event_id),
                    "created_at": utc_now(),
                }
            ]
        )
        return AskUserCacheEntry(
            id=entry_id,
            session_id=data.session_id,
            source_completed_event_id=data.source_completed_event_id,
        )

    async def find_nearest(
        self,
        *,
        session_id: UUID,
        vector: list[float],
        max_distance: float,
    ) -> AskUserCacheEntry | None:
        table = await self._get_table(vector_size=len(vector))
        query = await table.search(vector, vector_column_name="vector")
        rows = await query.where(f"session_id = '{session_id}'").limit(1).to_list()
        if not rows:
            return None

        row = rows[0]
        if float(row["_distance"]) > max_distance:
            return None

        return AskUserCacheEntry(
            id=UUID(row["id"]),
            session_id=UUID(row["session_id"]),
            source_completed_event_id=UUID(row["source_completed_event_id"]),
        )

    async def _get_table(self, *, vector_size: int) -> AsyncTable:
        if vector_size <= 0:
            raise ValueError("Ask-user cache vectors must not be empty")

        connection = await self._vector_db.connect()
        table_names = await connection.table_names()
        if ASK_USER_CACHE_TABLE not in table_names:
            return await connection.create_table(
                ASK_USER_CACHE_TABLE,
                schema=_table_schema(vector_size),
                exist_ok=True,
            )

        table = await connection.open_table(ASK_USER_CACHE_TABLE)
        _raise_if_vector_size_mismatch(schema=await table.schema(), expected_size=vector_size)
        return table


def _table_schema(vector_size: int) -> pa.Schema:
    return pa.schema(
        [
            pa.field("id", pa.string(), nullable=False),
            pa.field("session_id", pa.string(), nullable=False),
            pa.field("vector", pa.list_(pa.float32(), vector_size), nullable=False),
            pa.field("source_completed_event_id", pa.string(), nullable=False),
            pa.field("created_at", pa.timestamp("us", tz="UTC"), nullable=False),
        ]
    )


def _raise_if_vector_size_mismatch(*, schema: pa.Schema, expected_size: int) -> None:
    vector_type = schema.field("vector").type
    if not pa.types.is_fixed_size_list(vector_type) or vector_type.list_size != expected_size:
        raise ValueError(
            f"Ask-user cache table vector size does not match embedding size: "
            f"expected {expected_size}, found {vector_type}"
        )
