# Generated by Django 5.0.1 on 2024-03-01 06:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0009_alter_contest_end_time_alter_contest_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contest',
            name='end_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 3, 2, 6, 10, 20, 446937, tzinfo=datetime.timezone.utc)),
        ),
    ]
