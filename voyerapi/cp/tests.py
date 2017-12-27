from django.test import TestCase, Client

# Create your tests here.

from jobs.models import Job, JobMetadata
from inventory.models import Inventory
from inventory.lib import inventory
from .lib import checkpoint
from .lib import utils
from django.core.urlresolvers import reverse
from rest_framework import status
from knox.models import AuthToken
from rest_framework.test import APITestCase, APIClient
from .models import CPFirewall
from identity.models import User


class CPProccessRawInventoryTest(APITestCase):
    """
    Run raw inventory process test
    """
    #fixtures = ('fixtures-job', 'fixtures-meta')
    fixtures = ('fixtures-job', 'fixtures-inventory')

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
        inventory.process_inventory(self.uuid)
        self.inventory = Inventory.objects.filter(job__uuid=self.uuid)
        self.checkpoint = checkpoint.Checkpoint(self.uuid)

        # def test_get_inventory(self):
        #     self.inventory = utils.get_inventory(self.uuid)
        #     self.assertIsNotNone(self.inventory)

    ## UTIL TESTS

    # def test_get_network_objects(self):
    #     self.network_objects = utils.get_network_objects(self.inventory)
    #     print(self.network_objects)
    #     for network in self.network_objects:
    #         print(network)
    #     self.assertIsNotNone(self.network_objects)
    # #
    # def test_get_host_objects(self):
    #     self.host_objects = utils.get_host_objects(self.inventory)
    #     # print(self.host_objects)
    #     for host in self.host_objects:
    #         print(host)
    #     self.assertIsNotNone(self.host_objects)
    # #
    # # def test_get_group_objects(self):
    # #     self.group_objects = utils.get_group_objects(self.inventory)
    # #     print(self.group_objects)
    # #     self.assertIsNotNone(self.group_objects)
    # def test_get_service_objects(self):
    #     self.service_objects = utils.get_tcp_services(self.inventory)
    #     print(self.service_objects)
    #     self.assertIsNotNone(self.service_objects)
    #
    #     # def test_get_inventory_view(self):
    #     #     client = APIClient()
    #     #     token = AuthToken.objects.create(self.user)
    #     #     result = checkpoint.process_inventory(self.uuid)
    #     #     response = client.get('/api/v1/inventory/{}'.format(self.uuid), format='json',
    #     #                           HTTP_AUTHORIZATION="Token %s" % token)
    #     #
    #     #     self.assertEqual(response.status_code, 200)
    # def test_get_access_rules(self):
    #     self.layer = "PIPELINE Network"
    #     self.access_rules = utils.get_access_rules(self.inventory, self.layer)
    #     print(self.inventory)
    #     for rule in self.access_rules:
    #         print(rule)
    #         self.assertIsNotNone(self.access_rules)
    ## CLASS TESTS
    # def test_initialise(self):
    #     self.checkpoint.connect()
    #     self.checkpoint.initialise()
    # def test_purge(self):
    #     self.checkpoint.connect()
    #     self.checkpoint.purge()
    # def test_get_access_rules(self):
    #     self.checkpoint.connect()
    #     self.checkpoint.purge()

    def test_cleanup(self):
        self.checkpoint.connect()
        self.checkpoint.disconnect()
    # def test_wait_condition(self):
    #     self.checkpoint.connect()
    #     self.checkpoint.manager.verify_policy("PIPELINE")

