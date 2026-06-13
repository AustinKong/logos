from datetime import UTC, datetime

UTC_EPOCH = datetime.fromtimestamp(0, UTC)


def utc_now() -> datetime:
    return datetime.now(UTC)
