import time
import datetime
from django.utils import timezone


def to_epoch(value: datetime.datetime) -> int:
    """Convert datetime to integer (epoch time)."""
    return int(time.mktime(value.timetuple()))


def from_epoch(value: int) -> datetime.datetime:
    """Convert integer (epoch time) to a datetime."""
    if value is None:
        return None
    return timezone.make_aware(datetime.datetime.fromtimestamp(value), timezone.get_current_timezone())