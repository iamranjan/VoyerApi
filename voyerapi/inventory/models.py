from django.contrib.postgres.fields import JSONField
from django.db import models
from jobs.models import Job
import uuid


# Create your models here.
class Inventory(models.Model):
    """
    Inventory object associated with a given job build
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, related_name='inv', on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    hostname = models.CharField(max_length=80)
    body = JSONField(default=dict())

    # TODO: add more specific categories here such as Networks, Interfaces, Metrics etc
    def __str__(self):
        return 'UUID:{}, NAME:{}'.format(self.uuid, self.name)
