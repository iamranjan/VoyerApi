def remove_address(x):
    """
    remove address from network dictionary as to enable a unique filter to be applied across
    networks that are in the inventory
    :param x: network dictionary i.e
    {
    'network': '192.168.71.0',
    'address': '192.168.71.1',
    'netmask': '255.255.255.0'
    'name': 'VM_MGMT',
    }
    :return: dictionary with 'address' key removed
    """
    return {
        'subnet': x['network'],
        'subnet-mask': x['netmask'],
        'name': x['name'],
    }


def make_host_object(x, y):
    """
    Create host object from inventory body
    :param x: Inventory
    : param y: Inventory.body.network iterator
    :return:
    """
    return {
        "name": "{}-{}".format(x.name, y['name']),
        "ip-address": y['address'],
        "groups": x.body['groups'][0]
    }


def get_network_objects(inventory):
    """
    From the inventory items determine the corresponding network objects that should be created
    :param inventory:
    :return:
    """

    networks = sum(filter(None, map(
        lambda x: list(map(lambda y: remove_address(y), x.body['networks'])) if x.body.get("networks") else None,
        inventory)), [])

    networks = filter(lambda x: x['name'] != "localhost", networks)

    unique_networks = [dict(y) for y in set(tuple(x.items()) for x in networks)]
    return unique_networks


def get_tcp_services(inventory):
    """
    From the inventory determine all of the required services that should exist and their corresponding ports
    :param inventory:
    :return: [
    {
    "name": "KIBANA",
    "port": "5601"
    },
    ....
    """
    service_map = {
        80: {
            "service": "http",
        },
        443: {
            "service": "https",
        },
        9200: {
            "service": "elasticsearc",
        },
        5601: {
            "service": "kibana",
        },
        7480: {
            "service": "s3",
        },
        9090: {
            "service": "prometheus",
        },
        5514: {
            "service": "logstash-syslog-high-port",
        },
        514: {
            "service": "syslog",
        },
        8080: {
            "service": "RESTful",
        }
    }

    def make_service(y):
        """

        :param y: port integer
        :return:
        """
        if service_map.get(y):
            return {
                "name": service_map[y]['service'],
                "port": str(y),
            }
        else:
            return None

    services = filter(None, sum(filter(None, map(
        lambda x: list(map(lambda y: make_service(y), x.body['port'])) if x.body.get("port") else None,
        inventory)), []))
    unique_service = [dict(y) for y in set(tuple(x.items()) for x in services)]
    return unique_service


def get_host_objects(inventory):
    """
    From the inventory items determine the corresponding network objects that should be created
    :param inventory:
    :return:
    """
    hosts = sum(filter(None, map(
        lambda x: list(map(lambda y: make_host_object(x, y), x.body['networks'])) if x.body.get("networks") else None,
        inventory)), [])
    hosts = filter(lambda x: "127.0.0.1" not in x['ip-address'], hosts)

    unique_hosts = [dict(y) for y in set(tuple(x.items()) for x in hosts)]
    unique_hosts.append({
        "name": "localhost",
        "ip-address": "127.0.0.1",
    })
    return unique_hosts


def get_group_objects(inventory):
    """
    From the inventory items determine the corresponding group objects that should be created and also manages the
    formatting of the item structure to ensure that it confirms to the requirements of the management API. E.G.
    group = {
        "name": "EXAMPLE_GROUP"
        }|
    :param inventory:
    :return:
    """

    def make_group(x):
        return [{"name": group} for group in x.body["groups"]] if x.body.get("groups") else None

    groups = sum(filter(None, map(make_group, inventory)), [])
    unique_hosts = [dict(y) for y in set(tuple(x.items()) for x in groups)]
    return unique_hosts


def get_access_rules(inventory, layer):
    """
    The crux IP right here:
    Attempt to determine the access rules that shoulde exist on the firewall according to a set of highly advanced
    heuristics, only possible because of the end-to-end topological awareness of the SCAPI service.
    :param inventory:
    :return:
    """

    def is_external(x):
        return "EXTERNAL" in x.body['visibility']

    def get_services(y):
        service_map = {
            80: {
                "service": "http",
            },
            443: {
                "service": "https",
            },
            9200: {
                "service": "elasticsearch",
            },
            5601: {
                "service": "kibana",
            },
            7480: {
                "service": "s3",
            },
            9090: {
                "service": "prometheus",
            },
            5514: {
                "service": "logstash-syslog-high-port",
            },
            514: {
                "service": "syslog",
            },
            8080: {
                "service": "RESTful",
            }
        }
        services = []
        for port in y:
            services.append(service_map[port]['service'])
        return services

    rules = []
    # management access rule
    management = {
        "layer": layer,
        "position": "top",
        "name": "management access",
        "action": "accept",
        "source": ["localhost", "VM_MGMT"],
        "destination": ["vsec"],
        "service": ["https"],
        "track": 'log'
    }
    rules.append(management)

    external_inventory = list(filter(is_external, inventory))
    for item in external_inventory:
        rule = {
            "layer": layer,
            "position": "top",
            "name": item.name.split('.')[0],
            "action": "accept",
            "source": ["any"],
            "destination": list(map(lambda x: x['name'], item.body['networks'])),
            "service": get_services(item.body['port'])
        }
        rules.append(rule)

    print(external_inventory)

    return rules


def process_rule(rule):
    """
    Take rule in format that is ugly and make clean
    :param rule:
    stage1:

    {'uid': 'e60dd2b9-9f81-419b-a175-3cd12ad5be17',
    'name': 'demo-sc-elasticsearch-01', 'type':
    'access-rule', 'domain': {'uid': '41e821a0-3720-11e3-aa6e-0800200c9fde',
    'name': 'SMC User', 'domain-type': 'domain'},
    'track': {'type': {'uid': '29e53e3d-23bf-48fe-b6b1-d59bd88036f9',
    'name': 'None', 'type': 'Track', 'domain': {'uid': 'a0bbbc99-adef-4ef8-bb6d-defdefdefdef',
    'name': 'Check Point Data', 'domain-type': 'data domain'}, 'color': 'none',
    'meta-info': {'validation-state': 'ok',
    'last-modify-time': {'posix': 1509229601985, 'iso-8601': '2017-10-28T18:26-0400'},
    'last-modifier': 'System', 'creation-time': {'posix': 1509229601985, 'iso-8601': '2017-10-28T18:26-0400'},
    'creator': 'System'}, 'tags': [], 'icon': 'General/globalsNone', 'comments': 'No tracking.', 'customFields': None},
    'per-session': False, 'per-connection': False, 'accounting': False, 'alert': 'none'},
    'layer': 'e17752f2-ef9a-4c9c-87c5-3738c56e4968', 'source': [{'uid': '97aeb369-9aea-11d5-bd16-0090272ccb30',
    'name': 'Any', 'type': 'CpmiAnyObject', 'domain': {'uid': 'a0bbbc99-adef-4ef8-bb6d-defdefdefdef',
    'name': 'Check Point Data', 'domain-type': 'data domain'}, 'color': 'black',
    'meta-info': {'validation-state': 'ok', 'last-modify-time': {'posix': 1509229588664,
    'iso-8601': '2017-10-28T18:26-0400'}, 'last-modifier': 'System',
    'creation-time': {'posix': 1509229588664, 'iso-8601': '2017-10-28T18:26-0400'},
    'creator': 'System'}, 'tags': [], 'icon': 'General/globalsAny', 'comments': None, 'display-name': '',
    'customFields': None}], 'source-negate': False,


    'destination': [{'uid': 'afd13fbc-6852-42d8-9e41-b0f7075827a5',
    'name': 'localhost', 'type': 'host', 'domain': {'uid': '41e821a0-3720-11e3-aa6e-0800200c9fde', 'name': 'SMC User',
    'domain-type': 'domain'}, 'ipv4-address': '127.0.0.1', 'interfaces': [], 'nat-settings': {'auto-rule': False},
    'groups': [], 'comments': '', 'color': 'black', 'icon': 'Objects/host', 'tags': [],
    'meta-info': {'lock': 'unlocked', 'validation-state': 'ok',
    'last-modify-time': {'posix': 1509272103129, 'iso-8601': '2017-10-29T06:15-0400'},
    'last-modifier': 'admin', 'creation-time': {'posix': 1509272103129, 'iso-8601': '2017-10-29T06:15-0400'},
    'creator': 'admin'}, 'read-only': False}, {'uid': '138ed1ce-4086-48b1-9ed4-4c95d92e24c1', 'name': 'VM_VM',
    'type': 'network', 'domain': {'uid': '41e821a0-3720-11e3-aa6e-0800200c9fde',
    'name': 'SMC User', 'domain-type': 'domain'}, 'broadcast': 'allow', 'subnet4': '10.1.1.0',
    'mask-length4': 24, 'subnet-mask': '255.255.255.0',
    'nat-settings': {'auto-rule': False}, 'groups': [],
    'comments': '', 'color': 'black', 'icon': 'NetworkObjects/network',
    'tags': [], 'meta-info': {'lock': 'unlocked',
    'validation-state': 'ok', 'last-modify-time': {'posix': 1509272092449, 'iso-8601': '2017-10-29T06:14-0400'},
    'last-modifier': 'admin',
    'creation-time': {'posix': 1509272092449, 'iso-8601': '2017-10-29T06:14-0400'}, 'creator': 'admin'},
    'read-only': False}, {'uid': '2085a4ee-ec19-4c3c-bfaa-f447d215da93', 'name': 'VM_MGMT', 'type': 'network',
    'domain': {'uid': '41e821a0-3720-11e3-aa6e-0800200c9fde', 'name': 'SMC User', 'domain-type': 'domain'},
    'broadcast': 'allow', 'subnet4': '192.168.71.0', 'mask-length4': 24, 'subnet-mask': '255.255.255.0',
    'nat-settings': {'auto-rule': False}, 'groups': [],
    'comments': '', 'color': 'black', 'icon': 'NetworkObjects/network', 'tags': [],
    'meta-info': {'lock': 'unlocked', 'validation-state': 'ok',
    'last-modify-time': {'posix': 1509272091847, 'iso-8601': '2017-10-29T06:14-0400'},
    'last-modifier': 'admin', 'creation-time': {'posix': 1509272091847, 'iso-8601': '2017-10-29T06:14-0400'},
    'creator': 'admin'}, 'read-only': False}], 'destination-negate': False,
    'service': [{'uid': '00fa9e44-0ab6-0f65-e053-08241dc22da2', 'name': 'Elasticsearch', 'type': 'application-site',
    'domain': {'uid': '8bf4ac51-2df7-40e1-9bce-bedbedbedbed', 'name': 'APPI Data', 'domain-type': 'data domain'},
    'application-id': 60515620, 'primary-category': 'Business Applications', 'description':
    'Elasticsearch is an open source search server. Elasticsearch provides distributed full text search engine and schema free JSON documents DB.',
    'risk': 'Low', 'user-defined': False, 'additional-categories': ['Opens ports', 'Low Risk',
    'Business Applications'], 'groups': [], 'comments': '', 'color': 'black', 'icon': '@app/60515620_2',
    'tags': [], 'meta-info': {'lock': 'unlocked', 'validation-state': 'ok',
    'last-modify-time': {'posix': 1509229645397, 'iso-8601': '2017-10-28T18:27-0400'},
    'last-modifier': 'System', 'creation-time': {'posix': 1509229645397, 'iso-8601': '2017-10-28T18:27-0400'},
     'creator': 'System'}, 'read-only': False}, {'uid': 'ec3e8b72-9460-4fcf-9b14-18dcac133164',
     'name': 'kibana', 'type': 'service-tcp', 'domain': {'uid': '41e821a0-3720-11e3-aa6e-0800200c9fde',
     'name': 'SMC User', 'domain-type': 'domain'}, 'port': '5601', 'match-by-protocol-signature': False,
     'override-default-settings': False, 'session-timeout': 3600, 'use-default-session-timeout': True,
     'match-for-any': True, 'sync-connections-on-cluster': True, 'aggressive-aging': {'enable': True,
     'timeout': 600, 'use-default-timeout': True, 'default-timeout': 0},
     'keep-connections-open-after-policy-installation': False, 'groups': [],
     'comments': '', 'color': 'black', 'icon': 'Services/TCPService', 'tags': [],
     'meta-info': {'lock': 'unlocked',
     'validation-state': 'ok', 'last-modify-time': {'posix': 1509265755488, 'iso-8601': '2017-10-29T04:29-0400'},
     'last-modifier': 'admin',
     'creation-time': {'posix': 1509265755488, 'iso-8601': '2017-10-29T04:29-0400'}, 'creator': 'admin'},
     'read-only': False}, {'uid': '97aeb443-9aea-11d5-bd16-0090272ccb30', 'name': 'https', 'type': 'service-tcp',
     'domain': {'uid': 'a0bbbc99-adef-4ef8-bb6d-defdefdefdef', 'name': 'Check Point Data', 'domain-type': 'data domain'},
     'port': '443', 'protocol': 'ENC-HTTP', 'match-by-protocol-signature': False, 'override-default-settings': False,
     'session-timeout': 3600, 'use-default-session-timeout': True, 'match-for-any': True,
     'sync-connections-on-cluster': True, 'aggressive-aging': {'enable': True, 'timeout': 60,
     'use-default-timeout': False, 'default-timeout': 60}, 'keep-connections-open-after-policy-installation': False,
     'groups': ['07e0f434-08a8-45fe-89a6-36fa4fbcb14d', '82bccbc2-603c-4d96-a59b-9c2b730efb5c'],
     'comments': 'HTTP protocol over TLS/SSL', 'color': 'red', 'icon': 'Services/TCPService', 'tags': [],
     'meta-info': {'lock': 'unlocked', 'validation-state': 'ok',
      'last-modify-time': {'posix': 1509229597079, 'iso-8601': '2017-10-28T18:26-0400'},
      'last-modifier': 'System', 'creation-time': {'posix': 1509229597079, 'iso-8601': '2017-10-28T18:26-0400'},
      'creator': 'System'}, 'read-only': False}, {'uid': '97aeb3d4-9aea-11d5-bd16-0090272ccb30',
      'name': 'http', 'type': 'service-tcp', 'domain': {'uid': 'a0bbbc99-adef-4ef8-bb6d-defdefdefdef',
      'name': 'Check Point Data', 'domain-type': 'data domain'}, 'port': '80',
      'protocol': 'HTTP', 'match-by-protocol-signature': False, 'override-default-settings': False,
      'session-timeout': 3600, 'use-default-session-timeout': True, 'match-for-any': True,
      'sync-connections-on-cluster': True, 'aggressive-aging': {'enable': True, 'timeout': 60,
      'use-default-timeout': False, 'default-timeout': 60}, 'keep-connections-open-after-policy-installation': False,
      'groups': ['07e0f434-08a8-45fe-89a6-36fa4fbcb14d', '82bccbc2-603c-4d96-a59b-9c2b730efb5c', '97aeb468-9aea-11d5-bd16-0090272ccb30'],
      'comments': 'Hypertext Transfer Protocol', 'color': 'forest green', 'icon': 'Services/TCPService', 'tags': [],
      'meta-info': {'lock': 'unlocked', 'validation-state': 'ok', 'last-modify-time': {'posix': 1509229595911, 'iso-8601': '2017-10-28T18:26-0400'},
      'last-modifier': 'System', 'creation-time': {'posix': 1509229595911, 'iso-8601': '2017-10-28T18:26-0400'}, 'creator': 'System'},
      'read-only': False}], 'service-negate': False, 'vpn': [{'uid': '97aeb369-9aea-11d5-bd16-0090272ccb30', 'name': 'Any',
      'type': 'CpmiAnyObject', 'domain': {'uid': 'a0bbbc99-adef-4ef8-bb6d-defdefdefdef', 'name': 'Check Point Data',
      'domain-type': 'data domain'}, 'color': 'black', 'meta-info': {'validation-state': 'ok', 'last-modify-time': {'posix': 1509229588664, 'iso-8601': '2017-10-28T18:26-0400'}, 'last-modifier': 'System', 'creation-time': {'posix': 1509229588664, 'iso-8601': '2017-10-28T18:26-0400'}, 'creator': 'System'}, 'tags': [], 'icon': 'General/globalsAny', 'comments': None, 'display-name': '', 'customFields': None}], 'action': {'uid': '6c488338-8eec-4103-ad21-cd461ac2c472', 'name': 'Accept', 'type': 'RulebaseAction', 'domain': {'uid': 'a0bbbc99-adef-4ef8-bb6d-defdefdefdef', 'name': 'Check Point Data', 'domain-type': 'data domain'}, 'color': 'none', 'meta-info': {'validation-state': 'ok', 'last-modify-time': {'posix': 1509229602117, 'iso-8601': '2017-10-28T18:26-0400'}, 'last-modifier': 'System', 'creation-time': {'posix': 1509229602117, 'iso-8601': '2017-10-28T18:26-0400'}, 'creator': 'System'}, 'tags': [], 'icon': 'Actions/actionsAccept', 'comments': 'Accept', 'display-name': 'Accept', 'customFields': None}, 'action-settings': {'enable-identity-captive-portal': False}, 'content': [{'uid': '97aeb369-9aea-11d5-bd16-0090272ccb30', 'name': 'Any', 'type': 'CpmiAnyObject', 'domain': {'uid': 'a0bbbc99-adef-4ef8-bb6d-defdefdefdef', 'name': 'Check Point Data', 'domain-type': 'data domain'}, 'color': 'black', 'meta-info': {'validation-state': 'ok', 'last-modify-time': {'posix': 1509229588664, 'iso-8601': '2017-10-28T18:26-0400'}, 'last-modifier': 'System', 'creation-time': {'posix': 1509229588664, 'iso-8601': '2017-10-28T18:26-0400'}, 'creator': 'System'}, 'tags': [], 'icon': 'General/globalsAny', 'comments': None, 'display-name': '', 'customFields': None}], 'content-negate': False, 'content-direction': 'any', 'time': [{'uid': '97aeb369-9aea-11d5-bd16-0090272ccb30', 'name': 'Any', 'type': 'CpmiAnyObject', 'domain': {'uid': 'a0bbbc99-adef-4ef8-bb6d-defdefdefdef', 'name': 'Check Point Data', 'domain-type': 'data domain'}, 'color': 'black', 'meta-info': {'validation-state': 'ok', 'last-modify-time': {'posix': 1509229588664, 'iso-8601': '2017-10-28T18:26-0400'}, 'last-modifier': 'System', 'creation-time': {'posix': 1509229588664, 'iso-8601': '2017-10-28T18:26-0400'}, 'creator': 'System'}, 'tags': [], 'icon': 'General/globalsAny', 'comments': None, 'display-name': '', 'customFields': None}], 'custom-fields': {'field-1': '', 'field-2': '', 'field-3': ''}, 'meta-info': {'lock': 'unlocked', 'validation-state': 'ok', 'last-modify-time': {'posix': 1509272110707, 'iso-8601': '2017-10-29T06:15-0400'}, 'last-modifier': 'admin', 'creation-time': {'posix': 1509272110566, 'iso-8601': '2017-10-29T06:15-0400'}, 'creator': 'admin'}, 'comments': '', 'enabled': True, 'install-on': [{'uid': '6c488338-8eec-4103-ad21-cd461ac2c476', 'name': 'Policy Targets', 'type': 'Global', 'domain': {'uid': 'a0bbbc99-adef-4ef8-bb6d-defdefdefdef', 'name': 'Check Point Data', 'domain-type': 'data domain'}, 'color': 'none', 'meta-info': {'validation-state': 'ok', 'last-modify-time': {'posix': 1509229601925, 'iso-8601': '2017-10-28T18:26-0400'}, 'last-modifier': 'System', 'creation-time': {'posix': 1509229601925, 'iso-8601': '2017-10-28T18:26-0400'}, 'creator': 'System'}, 'tags': [], 'icon': 'General/globalsAny', 'comments': 'The policy target gateways', 'customFields': None}]}}


    :return:
    """

    def make_destination(x):
        # print(x)
        if x.get("ipv4-address") and x.get('mask-length4'):
            return {
                "name": x['name'],
                "ipv4-address": x['ipv4-address'],
                "prefix": x['mask-length4'],
            }
        elif x.get("ipv4-address") and not x.get('mask-length4'):
            return {
                "name": x['name'],
                "ipv4-address": x['ipv4-address'],
            }
        elif x.get("subnet4") and x.get('mask-length4') and not x.get("ipv4-address"):
            return {
                "name": x['name'],
                "subnet": x['subnet4'],
                "prefix": x['mask-length4'],
            }
        else:
            return {
                "name": x['name']
            }

    def make_source(x):
        return {"name": x['name'], "color": x['color']}

    def make_service(x):
        return {"name": x['name'], "color": x['color']}

    return {'name': rule['name'], 'type': rule['type'],
                  'sources': (list(map(make_source, rule['source'])),),
                  'services': (list(map(make_service, rule['service'])),),
                  'destination': (list(map(make_destination, rule['destination'])),),
                  'action': rule['action']['name']}
