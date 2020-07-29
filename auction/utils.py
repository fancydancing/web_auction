import time
import datetime
from django.utils import timezone
from celery import current_app


def to_epoch(value: datetime.datetime) -> int:
    """Convert datetime to integer (epoch time)."""
    return int(time.mktime(value.timetuple()))


def from_epoch(value: int) -> datetime.datetime:
    """Convert integer (epoch time) to a datetime."""
    if value is None:
        return None
    return timezone.make_aware(datetime.datetime.fromtimestamp(value), timezone.get_current_timezone())

def celery_send_ws_task(p):
    current_app.send_task('auction.tasks.celery_ws_send', args=[p])

def celery_send_email_task(subject: str, content: str, recipients: [str]):
    current_app.send_task('auction.tasks.task_send_email', args=[subject, content, recipients])

def celery_send_autobid_task():
    current_app.send_task('auction.tasks.task_autobid', args=[])