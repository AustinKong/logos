from datetime import datetime


def format_datetime(value: datetime) -> str:
    return value.astimezone().strftime("%Y-%m-%d %H:%M")


def format_time(value: datetime) -> str:
    return value.astimezone().strftime("%H:%M")
