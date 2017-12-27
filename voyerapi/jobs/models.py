from django.db import models
from django.contrib.postgres.fields import JSONField
# from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
import uuid


class Job(models.Model):
    username = models.TextField()
    job = models.CharField(max_length=256)
    jobNumber = models.IntegerField(default=-1)
    uuid = models.CharField(primary_key=True, max_length=100, unique=True, default=uuid.uuid4)
    status = models.TextField(default="STARTED")
    progress = models.IntegerField(default=0)
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)


class JobMetadata(models.Model):
    job = models.ForeignKey(Job, related_name='meta', on_delete=models.CASCADE)
    kafka = JSONField(default=dict())
    s3 = JSONField(default=dict())
    firewall = JSONField(default=dict())
    stdout = models.TextField()
    inventory = JSONField(default=dict())


# Create your models here.
class Tag(models.Model):
    name = models.TextField()
    job = models.ForeignKey(Job, related_name='tags', on_delete=models.CASCADE)
