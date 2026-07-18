from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Uuid as SQLAlchemyUuid
from sqlalchemy.orm import Mapped, mapped_column

from api.db.types import UTCDateTime
from api.shared.time import utc_now


class UUIDMixin:
    id: Mapped[UUID] = mapped_column(SQLAlchemyUuid, primary_key=True, default=uuid4)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now, onupdate=utc_now)
