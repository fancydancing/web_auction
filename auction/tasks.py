# Create your tasks here
from __future__ import absolute_import, unicode_literals

from celery import shared_task
from celery.task import periodic_task
from celery.schedules import crontab
from datetime import timedelta

@shared_task
def task_send_email(some_text=None):
    print('CELERY TASK: {}'.format(some_text))


@periodic_task(run_every=(timedelta(seconds=10)), name='task_every_min_name')
def task_every_min():
    print('CELERY EVERY MIN: {}'.format('test'))
