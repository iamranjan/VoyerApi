from django.test import TestCase, Client

# Create your tests here.

from jobs.models import Job, JobMetadata
from inventory.lib import inventory
from django.core.urlresolvers import reverse
from rest_framework import status
from knox.models import AuthToken
from rest_framework.test import APITestCase, APIClient
from .models import Inventory
from identity.models import User
import json


class ProccessRawInventoryTest(APITestCase):
    """
    Run raw inventory process test
    """
    fixtures = ('fixtures-job', 'fixtures-meta')

    def setUp(self):
        self.uuid = "7c32d60d-6312-42f6-a73a-22da56b07372"
        self.job = Job.objects.get(uuid=self.uuid)
        self.testUsername = 'test_user'
        self.testPassword = 'test_user_password'
        self.email = "test_user@gmail.com"
        self.first_name = "test"
        self.last_name = "user"
        # create a test user
        self.user = User.objects.create_user(username=self.testUsername,
                                             password=self.testPassword,
                                             email=self.email,
                                             first_name=self.first_name,
                                             last_name=self.last_name)

    def test_get_raw_inventory(self):
        self.job = Job.objects.get(uuid=self.uuid)
        self.metadata = JobMetadata.objects.get(job=self.job)

    def test_process_raw_inventory(self):
        result = inventory.process_inventory(self.uuid)
        # get inventory via job:
        # print(Job.objects.get(uuid=self.uuid).inv.get_queryset())
        # get inventory via inventory:
        # print(Inventory.objects.filter(job__uuid=self.uuid))
        self.assertTrue(result)

    def test_get_inventory_view(self):
        client = APIClient()
        token = AuthToken.objects.create(self.user)
        result = inventory.process_inventory(self.uuid)
        response = client.get('/api/v1/inventory/{}'.format(self.uuid), format='json',
                              HTTP_AUTHORIZATION="Token %s" % token)

        # for item in response.json():
        #     print(json.dumps(item, indent=4, sort_keys=True))

        self.assertEqual(response.status_code, 200)

    def test_get_subset_inventory_view(self):
        client = APIClient()
        token = AuthToken.objects.create(self.user)
        result = inventory.process_inventory(self.uuid)
        response = client.get('/api/v1/inventory/{}/{}'.format(self.uuid, "cp"), format='json',
                              HTTP_AUTHORIZATION="Token %s" % token)

        # for item in response.json():
        #     print(json.dumps(item, indent=4, sort_keys=True))

        self.assertEqual(response.status_code, 200)
