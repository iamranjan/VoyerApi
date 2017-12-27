from functools import reduce

from jobs.models import Job, JobMetadata
from inventory.models import Inventory
import re


def process_inventory(uuid):
    """
    Takes a given uuid and looks up the corresponding job metadata content. With the content available
    the function will process it into the required inventory objects for usage by other applications within the API.
    :param uuid: uuid corresponding to the pk of the job
    :return:
    """
    try:
        job = Job.objects.get(uuid=uuid)
        job_metadata = JobMetadata.objects.get(job=job)
    except JobMetadata.DoesNotExist:
        print("PROCESS_INVENTORY:NOT_FOUND:UUID:{}".format(uuid))
        return False
    # try:
    localhost = "127.0.0.1"
    raw_inventory = job_metadata.inventory
    clean_inventory = dict(filter(lambda x: 'mgmt.pants.net' in x[0], raw_inventory.items()))
    for item, content in clean_inventory.items():
        if content.get("ansible_interfaces"):
            networks = list(filter(lambda x: localhost not in x['address'], filter(None, map(lambda x: parse_ansible_interface_body(content["ansible_{}".format(x)]),
                                content["ansible_interfaces"]))))
        else:
            networks = {}
        meta_mapping = get_mapping(item)
        body = {
                 "management_address": content["ansible_eth0"]["ipv4"]["address"] if content.get("ansible_eth0") else item,
                 "port": sum(list(map(lambda x: x['ports'], meta_mapping)), []),
                 "services": list(map(lambda x: x['service'], meta_mapping)),
                 "groups": list(map(lambda x: x['group'], meta_mapping)),
                 "visibility": list(map(lambda x: x['visibility'], meta_mapping)),
                 "networks": networks,
                 }

        Inventory.objects.create(job=job,
                                 name=content["ansible_hostname"]
                                 if content.get("ansible_hostname") else item.split('.')[0],
                                 hostname=item,
                                 body=body
                                 )


    return True

    # except Exception as e:
    #     print("INVENTORY:PROCESS_INVENTORY:PROCESSING_FAILURE:PARSING:E:{}".format(e))
    #     return False


def get_mapping(hostname):
    """
    Attempt to determine the relavent ports for a given hostname
    i.e
    logstash uses 514, 5514 etc
    kafka uses 9092, 2181
    elasticsearch uses 9200,
    kibana uses 5601


    :param hostname:
    :return:
    """
    meta_map = [
        {
            "group": "BROKER",
            "service": "BROKER",
            "visibility": "INTERNAL",
            "name": "KAFKA",
            "pattern": "kafka|zookeeper",
            "ports": [9092, 2181, 9093],
        },
        {
            "group": "PROCESSOR",
            "service": "LOGSTASH",
            "visibility": "INTERNAL",
            "name": "LOGSTASH",
            "pattern": "ls|logstash",
            "ports": [514, 5514, 8080],
        },
        {
            "group": "INDEX_STORAGE",
            "service": "ELASTICSEARCH",
            "name": "ELASTICSEARCH",
            "visibility": "EXTERNAL",
            "pattern": "es|elasticsearch",
            "ports": [9200],
        },
        {
            "group": "GRAPHING",
            "service": "KIBANA",
            "visibility": "EXTERNAL",
            "name": "KIBANA",
            "pattern": "kibana|elasticsearch",
            "ports": [5601, 443, 80],
        },
        {
            "group": "MONITORING",
            "service": "PROMETHEUS",
            "visibility": "EXTERNAL",
            "name": "PROMETHEUS",
            "pattern": "prom|prometheus",
            "ports": [9090],
        },
        {
            "group": "LOGGING",
            "service": "SYSLOG",
            "visibility": "INTERNAL",
            "name": "SYSLOG",
            "pattern": "syslog|rsyslog",
            "ports": [514, 2181, 9093],
        },
        {
            "group": "ARCHIVE",
            "service": "ARCHIVE",
            "visibility": "EXTERNAL",
            "name": "S3",
            "pattern": "s3|rgw|ceph",
            "ports": [7480, 8080],
        },
        {
            "group": "FIREWALL",
            "service": "CHECKPOINT",
            "visibility": "INTERNAL",
            "name": "CHECKPOINT",
            "pattern": "sc\-cp|checkpoint",
            "ports": [-1],
        },
        {
            "group": "LOADBALANCER",
            "service": "F5",
            "visibility": "EXTERNAL",
            "name": "F5",
            "pattern": "(sc\-f5)|(f5\-lb)|(f5-loadbalance)",
            "ports": [-1],
        }
    ]

    matches = []
    for pattern in meta_map:
        match = re.search(pattern['pattern'], hostname, re.MULTILINE)
        if match:
            matches.append(pattern)
        else:
            continue

    if matches:
        return matches
    else:
        return []


def parse_ansible_interface_body(body):
    """
    Parse body in the format:
    {
        "mtu": 65536,
        "ipv4": {
            "address": "127.0.0.1",
            "netmask": "255.0.0.0",
            "network": "127.0.0.0",
            "broadcast": "host"
        },
        "ipv6": [
            {
                "scope": "host",
                "prefix": "128",
                "address": "::1"
            }
            ...
    }
    :param body:
    :return: { "network": "xxxx", "address": "xxxx", "netmask": "xxxxx" }
    """
    try:
        return {
            "network": body["ipv4"]["network"],
            "address": body["ipv4"]["address"],
            "netmask": body["ipv4"]["netmask"],
            "name": get_network_name(body["ipv4"]["network"]),
        }
    except Exception as e:
        # print("INTERFACE:BODY:PARSE:FAILURE:E:{}:BODY:{}".format(e, body))
        return None


def get_network_name(network):
    """
    network name can be resolved via a preset mapping of subnets and names in say openstack
    :param network: x.x.x.x
    :return: string: NAME
    """
    network_name_map = [
        {
            "network": "10.1.1.0",
            "name": "VM_VM"
        },
        {
            "network": "10.2.2.0",
            "name": "F5_INSIDE"
        },
        {
            "network": "192.168.71.0",
            "name": "VM_MGMT"
        },
        {
            "network": "192.168.110.0",
            "name": "FP"
        },
        {
            "network": "192.168.70.0",
            "name": "MGMT"
        },
    ]
    matches = []
    for pattern in network_name_map:
        match = pattern['network'] == network
        if match:
            matches.append(pattern["name"])
        else:
            continue

    if matches:
        if len(matches) == 1:
            return matches[0]
        else:
            return "UNKNOWN-MULTI-MATCH"
    else:
        return "localhost"
