# Generated by Django 5.0.1 on 2024-02-19 08:45

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0003_alter_contest_end_time_alter_contest_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contest',
            name='end_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 20, 8, 45, 33, 50778, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='contest',
            name='title',
            field=models.CharField(default='2024-02-19', max_length=15),
        ),
    ]
