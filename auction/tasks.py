# Create your tasks here
from __future__ import absolute_import, unicode_literals

from django.core.mail import EmailMessage
from django.utils import timezone

from celery import shared_task
from celery.task import periodic_task
from celery.schedules import crontab
from datetime import timedelta
from .auction import check_deadlines, check_autobidding
from .models import Item, Bid


@shared_task
def task_send_email(subject, content, recipient_list):
    print('CELERY TASK: sending email')
    sender = 'webauctiontesting@mail.ru'
    msg = EmailMessage(subject, content, sender, recipient_list)
    msg.content_subtype = 'html'
    msg.send()

@shared_task
def task_autobid_on_item(item_id, price):
    print('CELERY TASK: autobidding')
    users_emails = check_autobidding(item_id, price)

    # email_subject = 'Autobid was set on an item'
    # email_content = ''
    # for email in users_emails:

    # task_send_email.delay(email_subject, email_content, email_recipients)

@periodic_task(run_every=(timedelta(minutes=1)), name='Check deadlines')
def task_check_deadlines():
    print('CELERY TASK: checking deadlines')
    awards = check_deadlines()
    email_subject = 'Congratulations!'

    for award in awards:
        email_content = 'You have been awarded an item ' + award.get('item') + ' at a price ' + str(award.get('price')) + '. Come to webauction.herokuapp.com for more opportunities!'
        email_recipients = [award.get('email')]
        task_send_email.delay(email_subject, email_content, email_recipients)

