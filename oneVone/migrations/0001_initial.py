# Generated by Django 5.0.1 on 2024-02-19 08:45

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('problem', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OneVOne',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='untitled', max_length=15)),
                ('description', models.TextField(default='no description')),
                ('duration', models.IntegerField(default=600)),
                ('num_of_problem', models.IntegerField(default=5)),
                ('key', models.CharField(max_length=50, unique=True)),
                ('status', models.CharField(choices=[('created', 'created'), ('started', 'started'), ('ended', 'ended')], default='created', max_length=10)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('primary_user_status', models.CharField(choices=[('waiting', 'waiting'), ('joined', 'joined'), ('left', 'left')], default='joined', max_length=10)),
                ('secondary_user_status', models.CharField(choices=[('waiting', 'waiting'), ('joined', 'joined'), ('left', 'left')], default='waiting', max_length=10)),
                ('primary_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='primary_user', to=settings.AUTH_USER_MODEL)),
                ('secondary_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='secondary_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OneVOneProblem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('problem_number', models.IntegerField(default=1)),
                ('oneVone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='oneVone.onevone')),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='problem.problem')),
            ],
        ),
        migrations.CreateModel(
            name='OneVOneSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('oneVone_problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='oneVone.onevoneproblem')),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='problem.submission')),
            ],
        ),
    ]