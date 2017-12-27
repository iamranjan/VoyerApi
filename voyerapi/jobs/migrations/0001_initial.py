# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('username', models.TextField()),
                ('job', models.CharField(max_length=256)),
                ('jobNumber', models.IntegerField(default=-1)),
                ('uuid', models.CharField(default=uuid.uuid4, max_length=100, primary_key=True, serialize=False, unique=True)),
                ('status', models.TextField(default='STARTED')),
                ('progress', models.IntegerField(default=0)),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
            ],
        ),
        migrations.CreateModel(
            name='JobMetadata',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kafka', django.contrib.postgres.fields.jsonb.JSONField(default={})),
                ('s3', django.contrib.postgres.fields.jsonb.JSONField(default={})),
                ('firewall', django.contrib.postgres.fields.jsonb.JSONField(default={})),
                ('stdout', models.TextField()),
                ('inventory', django.contrib.postgres.fields.jsonb.JSONField(default={})),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meta', to='jobs.Job')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='jobs.Job')),
            ],
        ),
    ]
