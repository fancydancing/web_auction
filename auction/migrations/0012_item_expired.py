# Generated by Django 3.0.8 on 2020-07-23 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0011_auto_20200723_1530'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='expired',
            field=models.BooleanField(default=False),
        ),
    ]
