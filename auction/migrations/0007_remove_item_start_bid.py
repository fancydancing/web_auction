# Generated by Django 2.0.4 on 2020-07-02 12:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0006_auto_20200702_1330'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='start_bid',
        ),
    ]
