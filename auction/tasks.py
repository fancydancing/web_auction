# Create your tasks here
from __future__ import absolute_import, unicode_literals

from django.core.mail import EmailMessage
from django.utils import timezone

from celery import shared_task
from celery.task import periodic_task
from celery.schedules import crontab
from datetime import timedelta
from .auction import check_deadlines
from .models import Item, Bid


@shared_task
def task_send_email(subject, content, sender, recipient_list):
    print('CELERY TASK: sending email')
    msg = EmailMessage(subject, content, sender, recipient_list)
    msg.content_subtype = 'html'
    msg.send()


@periodic_task(run_every=(timedelta(minutes=1)), name='Check deadlines')
def task_check_deadlines():
    print('CELERY TASK: checking deadlines')
    awards = check_deadlines()
    email_subject = 'Congratulations!'
    email_sender = 'webauctiontesting@mail.ru'

    for award in awards:
        email_content = 'You have been awarded an item ' + award.get('item') + ' at a price ' + str(award.get('price')) + '. Come to webauction.herokuapp.com for more opportunities!'
        email_recipients = [award.get('email')]
        task_send_email.delay(email_subject, email_content, email_sender, email_recipients)

