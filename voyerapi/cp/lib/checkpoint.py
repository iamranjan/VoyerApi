from jobs.models import Job, JobMetadata
from inventory.models import Inventory
import re
from .config import PROPERTIES
from .api import CheckpointAPIManager
from .utils import *
import time
from .tasks import cleanup as async_cleanup
from celery import task
from celery.utils.log import get_task_logger


class Checkpoint:
    """
    Highest level class for managing the checkpoint firewall and interfacing between the checkpoint management API and
    the SCAPI endpoint.
    """

    def __init__(self, uuid):
        self.uuid = uuid
        self.cp_inventory, self.inventory = self.get_inventory()
        self.username = PROPERTIES['username']
        self.password = PROPERTIES['password']
        self.gateways = [PROPERTIES['gateway']]
        self.policies = [PROPERTIES['policy_package']]
        self.layers = [PROPERTIES['layer']]
        self.mode = PROPERTIES['mode']
        self.hostname = self.get_host()
        self.manager = None

    def connect(self):
        """
        Connect/instatiate APIManagement and other related content
        :return:
        """
        self.manager = CheckpointAPIManager(self.hostname, self.username, self.password)

    def disconnect(self):
        """
        Initialise an asychronous logout call and ensure that sessions are cleaned up correctly.
        :return:
        """
        if self.manager:
            async_cleanup.delay(self.uuid)
        else:
            self.connect()
            async_cleanup.delay(self.uuid)


    def get_inventory(self):
        """
        Get inventory items corresponding to job UUID
        :param uuid: job uuid
        :return:
        """
        try:
            job = Job.objects.get(uuid=self.uuid)
            inventory = Inventory.objects.filter(job__uuid=self.uuid)
            cp_inventory = Inventory.objects.get(job__uuid=self.uuid, body__services__0="CHECKPOINT")
            return cp_inventory, inventory
        except Inventory.DoesNotExist:
            print("PROCESS_INVENTORY:NOT_FOUND:UUID:{}".format(self.uuid))
            return None, None

    def get_host(self):
        """
        Resolve the hostname to be used to manage the given firewall instance
        """
        if self.mode == "DEV":
            return "localhost"
        else:
            return "demo-sc-cp-01.mgmt.pants.net"
            #return self.cp_inventory.hostname

    def initialise(self):
        """
        Initialise the checkpoint firewall with the day 0 configuration to enable basic management and the required
        configuration/policies to allow the pipeline to function.
        The initialisation process will assume that the inventory has been captured successfully and everything has been
        formatted into the inventory objects managed by SCAPI. These inventory objects will contain pertinent meta-data
        required to build access rules and also configure the gateway and other objects within checkpoints vSEC firewall.
        To baseline/initialise the checkpoint firewall we must build the following objects in the given order:
        1. Groups
        2. Networks
        2.1. Hosts (optional)
        3. Layers
        4. Access Rules
        5. Gateway
        :param uuid: uuid of a job
        :return:
        """
        if not self.manager:
            self.connect()
        self.manager.cleanup()
        groups = get_group_objects(self.inventory)
        networks = get_network_objects(self.inventory)
        hosts = get_host_objects(self.inventory)
        access_rules = get_access_rules(self.inventory, self.layers[0])
        tcp_services = get_tcp_services(self.inventory)
        for service in tcp_services:
            print(self.manager.add_tcp_service(service).json())
        for group in groups:
            print("CHECKPOINT:INITIALISE:ADD_GROUP:{}".format(group["name"]))
            self.manager.add_group(group)
        for network in networks:
            print("CHECKPOINT:INITIALISE:ADD_NETWORK:{}".format(network["name"]))
            print(self.manager.add_network(network).json())
        for host in hosts:
            print("CHECKPOINT:INITIALISE:ADD_HOST:{}".format(host["name"]))
            print(self.manager.add_host(host).json())

        for policy in self.policies:
            print("CHECKPOINT:INITIALISE:ADD_PACKAGE:{}".format(policy))
            print(self.manager.add_package(policy, self.gateways).json())
            print(self.manager.set_access_layer(self.layers[0]))
        for rule in access_rules:
            print("CHECKPOINT:INITIALISE:ADD_RULE:{}".format(rule))
            print(self.manager.add_access_rule(rule).json())
        self.manager.publish()
        time.sleep(5)
        for policy in self.policies:
            print("CHECKPOINT:INITIALISE:VERIFY_AND_INSTALL_POLICY:{}".format(policy))
            self.manager.verify_policy(policy)
            self.manager.install_policy(policy, self.gateways)
        self.manager.publish()
        self.manager.logout()

    def cleanup(self):
        if not self.manager:
            self.connect()
        sessions = self.manager.cleanup()
        print("CHECKPOINT:CLEANUP:DISCARDED_SESSIONS:{}".format(sessions))

    def purge(self):
        """
        Clear all initialisation configuration
        :return:
        """
        if not self.manager:
            self.connect()

        groups = get_group_objects(self.inventory)
        networks = get_network_objects(self.inventory)
        hosts = get_host_objects(self.inventory)
        payload = lambda x: {"name": x}
        for policy in self.policies:
            print("CHECKPOINT:INITIALISE:REMOVE_PACKAGE:{}".format(policy))
            print(self.manager.delete_package(policy, self.gateways).json())
        for group in groups:
            print("CHECKPOINT:INITIALISE:REMOVE_GROUP:{}".format(group["name"]))
            print(self.manager.delete_group(group).json())
        for host in hosts:
            print("CHECKPOINT:INITIALISE:REMOVE_HOST:{}".format(host["name"]))
            print(self.manager.delete_host(payload(host['name'])).json())
        for network in networks:
            print("CHECKPOINT:INITIALISE:REMOVE_NETWORK:{}".format(network["name"]))
            print(self.manager.delete_network(payload(network['name'])).json())

        for layer in self.layers:
            print("CHECKPOINT:INITIALISE:REMOVE_LAYER:{}".format(layer))
            self.manager.delete_access_layer(layer)

        for policy in self.policies:
            print("CHECKPOINT:INITIALISE:REMOVE_PACKAGE:{}".format(policy))
            self.manager.delete_package(policy, self.gateways)
        self.manager.publish()
        self.manager.cleanup()
        self.manager.logout()


    def get_rules(self):
        """
        Fetch the rules that are currently present in the firewall
        :return: List: access rule objects
        """

        return self.manager.show_rules(self.layers[0])



        # def initialise(uuid):
        #
        #     inventory = get_inventory(uuid)
        #
        #
        #     initialise_groups(inventory)
        #     initialise_networks(inventory)
        #     initialise_hosts(inventory)
        #     initialise_layers(inventory)
        #     initialise_gateway(inventory)
        #     initialise_gateway_interfaces(inventory)
        #     initialise_gateway_blades(inventory)
        #     initialise_access_rules(inventory)


# def initialise_networks(uuid):
#     """
#     :param uuid:
#     :return:
#     """
#     print(":INITIALISING_CHECKPOINT:NETWORKS:UUID:{}".format(uuid))
#
#
# def initialise_hosts(uuid):
#     """
#     :param uuid:
#     :return:
#     """
#     print(":INITIALISING_CHECKPOINT:HOSTS:UUID:{}".format(uuid))
#
#
# def initialise_layers(uuid):
#     """
#     :param uuid:
#     :return:
#     """
#     print(":INITIALISING_CHECKPOINT:LAYERS:UUID:{}".format(uuid))
#
#
# def initialise_gateway(uuid):
#     """
#     :param uuid:
#     :return:
#     """
#     print(":INITIALISING_CHECKPOINT:GATEWAY:UUID:{}".format(uuid))
#
#
# def initialise_gateway_interfaces(uuid):
#     """
#     :param uuid:
#     :return:
#     """
#     print(":INITIALISING_CHECKPOINT:GATEWAY_INTERFACES:UUID:{}".format(uuid))
#
#
# def initialise_gateway_blades(uuid):
#     """
#     :param uuid:
#     :return:
#     """
#     print(":INITIALISING_CHECKPOINT:GATEWAY_BLADES:UUID:{}".format(uuid))
#
#
# def initialise_access_rules(uuid):
#     """
#     :param uuid:
#     :return:
#     """
#     print(":INITIALISING_CHECKPOINT:ACCESS_RULES:UUID:{}".format(uuid))
