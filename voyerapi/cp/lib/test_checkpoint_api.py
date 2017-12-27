from .api import CheckpointAPIManager
import pytest
import time

"""MAPPING ORDER
GROUP -> HOST
"""


# ----------------------------------------------------------------------------------------
# ADD
# ----------------------------------------------------------------------------------------
@pytest.mark.checkpoint_clean
def test_clearAllSessions():
    manager = CheckpointAPIManager("localhost", "admin", "admin123")
    response = manager.login()
    print(response.json())
    response_discard_all = manager.discard_all_sessions()
    assert response_discard_all == True


@pytest.mark.checkpoint_login
def test_getCheckpointLogin():
    manager = CheckpointAPIManager("localhost", "admin", "admin123")
    response = manager.login()
    manager.logout()
    print(response.json())
    assert response.status_code == 200


@pytest.mark.checkpoint
def test_getCheckpointLogout():
    manager = CheckpointAPIManager("localhost", "admin", "admin123")
    manager.login()
    response_logout = manager.logout()
    print(response_logout.json())
    assert response_logout.status_code == 200


@pytest.mark.checkpoint
def test_getCheckpointAddGroup():
    manager = CheckpointAPIManager("localhost", "admin", "admin123")
    manager.login()
    test_group = {
        "name": "TEST_GROUP"
    }
    response_add_group = manager.add_group(test_group)
    print(response_add_group.json())
    manager.publish()
    time.sleep(10)
    manager.logout()
    assert response_add_group.status_code == 200


@pytest.mark.checkpoint
def test_CheckpointAddHost():
    manager = CheckpointAPIManager("localhost", "admin", "admin123")
    manager.login()
    test_host = {
        "name": "demo-sc-logstash-01",
        "groups": "TEST_GROUP",
        "ip-address": "192.168.71.22"
    }
    response_add_host = manager.add_host(test_host)
    print(response_add_host.json())
    manager.publish()
    manager.logout()
    assert response_add_host.status_code == 200


@pytest.mark.checkpoint
def test_CheckpointAddNetwork():
    manager = CheckpointAPIManager("localhost", "admin", "admin123")
    manager.login()
    test_network = {
        "name": "VM_MGMT",
        "subnet": "192.168.71.0",
        "subnet-mask": "255.255.255.0",

    }
    response_add_network = manager.add_network(test_network)
    manager.publish()
    manager.logout()
    assert response_add_network.status_code == 200


@pytest.mark.checkpoint
def test_AddAccessLayer():
    manager = CheckpointAPIManager("localhost", "admin", "admin123")
    manager.login()
    test_layer = {
        "name": "TEST_LAYER",
        "applications-and-url-filtering": "true",
        "content-awareness": "true",
        "detect-using-x-forward-for": "true",
        "mobile-access": "false"
    }
    response_add_test_layer = manager.add_access_layer(test_layer)
    print(response_add_test_layer.json())
    manager.publish()
    manager.logout()
    assert response_add_test_layer.status_code == 200


@pytest.mark.checkpoint
def test_AddAccessRule():
    manager = CheckpointAPIManager("localhost", "admin", "admin123")
    manager.login()
    test_layer = {
        "name": "TEST_RULE1",
        "layer": "TEST_LAYER",
        "position": "top",
        "source": "Any",
        "destination": ["TEST_GROUP", ],
        "service": ["https", "http"],
        "action": "accept",
        "track": 'log'
    }
    response_add_test_rule = manager.add_access_rule(test_layer)
    print(response_add_test_rule.json())
    manager.publish()
    manager.logout()
    assert response_add_test_rule.status_code == 200


@pytest.mark.checkpoint_policy
def test_AddPackage():
    manager = CheckpointAPIManager("localhost", "admin", "admin123")
    manager.login()
    test_package = {
            "name": "TEST_PACKAGE",
            "access": "true",
            "threat-prevention": "true",
            "installation-targets": [ "vsec" ]
        }
    response_add_test_policy= manager.add_package(test_package)
    print(response_add_test_policy.json())
    manager.publish()
    manager.logout()
    assert response_add_test_policy.status_code == 200
task_id = []

@pytest.mark.checkpoint_policy
def test_VerifyPolicy():
    manager = CheckpointAPIManager("localhost", "admin", "admin123")
    manager.login()
    test_package = {
            "policy-package": "TEST_PACKAGE",
        }
    response_verify_test_policy = manager.verify_policy(test_package)
    # task_id.append(response_verify_test_policy.json()['task-id'])
    # print(response_verify_test_policy.json())
    manager.publish()
    manager.logout()
    assert response_verify_test_policy is True


# @pytest.mark.checkpoint_policy
# def test_taskPoller():
#     manager = CheckpointAPIManager("localhost", "admin", "admin123")
#     manager.login()
#     test_package = {
#             "task-id": "TEST_PACKAGE",
#         }
#     response_verify_test_policy = manager.wait(task_id[0])
#     print(response_verify_test_policy.json())
#     manager.publish()
#     manager.logout()
#     assert response_verify_test_policy.status_code == 200

# ----------------------------------------------------------------------------------------
# SHOW/LIST
# ----------------------------------------------------------------------------------------

@pytest.mark.checkpoint
def test_getCheckpointListGroup():
    manager = CheckpointAPIManager("localhost", "admin", "admin123")
    manager.login()
    test_group = {
        "name": "TEST_GROUP"
    }
    response_list_group = manager.list_group(test_group)
    print(response_list_group.json())
    manager.logout()
    assert response_list_group.status_code == 200


@pytest.mark.checkpoint
def test_getCheckpointListHost():
    manager = CheckpointAPIManager("localhost", "admin", "admin123")
    manager.login()
    test_host = {
        "name": "demo-sc-logstash-01"
    }
    response_list_host = manager.show_host(test_host)
    print(response_list_host.json())
    manager.logout()
    assert response_list_host.status_code == 200


@pytest.mark.checkpoint_rule
def test_ShowAccessRule():
    manager = CheckpointAPIManager("localhost", "admin", "admin123")
    manager.login()
    test_layer = {
        "name": "demo-sc-elasticsearch-01",
        "layer": "PIPELINE Network",
    }
    response_show_test_rule = manager.show_access_rule(test_layer)
    print(response_show_test_rule.json())
    manager.publish()
    manager.logout()
    assert response_show_test_rule.status_code == 200


# @pytest.mark.checkpoint_rules
# def test_ShowAccessRuleBase():
#     manager = CheckpointAPIManager("localhost", "admin", "admin123")
#     manager.login()
#     test_rulebase = {
#         "name": "PIPELINE Network",
#         "offset": 0,
#         "limit": 20,
#         "details-level": "full",
#         "use-object-dictionary": "true"
#     }
#     response_show_test_rulebase = manager.show_access_rulebase(test_rulebase)
#     response = response_show_test_rulebase
#     for rule in response.json()['rulebase']:
#         print(rule)
#     manager.logout()
#     assert response_show_test_rulebase.status_code == 200

@pytest.mark.checkpoint_rules
def test_ShowAccessRules():
    manager = CheckpointAPIManager("localhost", "admin", "admin123")
    manager.login()
    test_layer = "PIPELINE Network"
    response_show_test_rules = manager.show_rules(test_layer)
    response = response_show_test_rules
    print(response[0])
    manager.logout()
    assert isinstance(response_show_test_rules, list)

@pytest.mark.checkpoint_service
def test_ShowTCPService():
    manager = CheckpointAPIManager("localhost", "admin", "admin123")
    manager.login()
    test_service = {
        "uid": "ec3e8b72-9460-4fcf-9b14-18dcac133164",
    }
    response_show_service = manager.show_tcp_service(test_service)
    response = response_show_service
    print(response.json())
    manager.logout()
    assert response_show_service.status_code == 200


# @pytest.mark.checkpoint_gw
# def test_getCheckpointSimpleGateways():
#     manager = CheckpointAPIManager("localhost", "admin", "admin123")
#     manager.login()
#     response_simple_gateways = manager.show_simple_gateways()
#     print(response_simple_gateways.json())
#     manager.logout()
#     assert response_simple_gateways.status_code == 200


@pytest.mark.checkpoint_gw
def test_getCheckpointSimpleGateway():
    manager = CheckpointAPIManager("localhost", "admin", "admin123")
    manager.login()
    test_gateway = {
        "name": "vsec"
    }
    response_simple_gateway = manager.show_simple_gateway(test_gateway)
    print(response_simple_gateway.json())
    manager.logout()
    assert response_simple_gateway.status_code == 200

@pytest.mark.checkpoint_policy
def test_showPackage():
    manager = CheckpointAPIManager("localhost", "admin", "admin123")
    manager.login()
    test_package = {
            "name": "TEST_PACKAGE",
        }
    response_show_test_policy= manager.show_package(test_package)
    print(response_show_test_policy.json())
    manager.publish()
    manager.logout()
    assert response_show_test_policy.status_code == 200


# ----------------------------------------------------------------------------------------
# DELETE OBJECTS:
# ----------------------------------------------------------------------------------------
@pytest.mark.checkpoint_policy
def test_deletePackage():
    manager = CheckpointAPIManager("localhost", "admin", "admin123")
    manager.login()
    test_package = {
            "name": "TEST_PACKAGE",
        }
    response_delete_test_policy= manager.delete_package(test_package)
    print(response_delete_test_policy.json())
    manager.publish()
    manager.logout()
    assert response_delete_test_policy.status_code == 200
@pytest.mark.checkpoint
def test_getCheckpointDeleteNetwork():
    manager = CheckpointAPIManager("localhost", "admin", "admin123")
    manager.login()
    test_network = {
        "name": "VM_MGMT"
    }
    response_delete_network = manager.delete_network(test_network)
    manager.publish()
    manager.logout()
    assert response_delete_network.status_code == 200


@pytest.mark.checkpoint_gw
def test_SetCheckpointSimpleGateway():
    manager = CheckpointAPIManager("localhost", "admin", "admin123")
    manager.login()
    test_gateway = {
        'name': 'vsec',
        'vpn': False,
        'application-control': False,
        'url-filtering': False,
        'ips': False,
        'content-awareness': False,
        'anti-bot': False,
        'anti-virus': False,
        'threat-emulation': False
    }
    response_set_simple_gateway = manager.set_simple_gateway(test_gateway)
    print(response_set_simple_gateway.json())
    manager.publish()
    manager.logout()
    assert response_set_simple_gateway.status_code == 200


@pytest.mark.checkpoint
def test_DeleteAccessRule():
    manager = CheckpointAPIManager("localhost", "admin", "admin123")
    # manager.login()
    test_layer = {
        "name": "TEST_LAYER",
    }
    response_delete_test_rule = manager.delete_access_rulebase(test_layer)
    manager.publish()
    manager.logout()
    assert isinstance(response_delete_test_rule, list)


@pytest.mark.checkpoint
def test_DeleteAccessLayer():
    manager = CheckpointAPIManager("localhost", "admin", "admin123")
    manager.login()
    test_layer = {
        "name": "TEST_LAYER",
    }
    response_add_test_layer = manager.delete_access_layer(test_layer)
    print(response_add_test_layer.json())
    manager.publish()
    manager.logout()
    assert response_add_test_layer.status_code == 200


@pytest.mark.checkpoint
def test_getCheckpointDeleteGroup():
    manager = CheckpointAPIManager("localhost", "admin", "admin123")
    manager.login()
    test_group = {
        "name": "TEST_GROUP"
    }
    # test_group = {
    #     'uid': 'c3bb071a-2c8b-4906-8573-3116ece58109'
    # }
    response_delete_group = manager.delete_group(test_group)
    manager.publish()
    manager.logout()
    assert response_delete_group.status_code == 200


@pytest.mark.checkpoint
def test_CheckpointDeleteHost():
    manager = CheckpointAPIManager("localhost", "admin", "admin123")
    manager.login()
    test_host = {
        "name": "demo-sc-logstash-01"
    }
    # # test_group = {
    # #     'uid': 'c3bb071a-2c8b-4906-8573-3116ece58109'
    # # }
    # time.sleep(1)
    # response_list_host = manager.show_host(test_host)
    # print(response_list_host.json())
    # time.sleep(5)
    # manager.logout()
    # manager.login()
    response_delete_host = manager.delete_host(test_host)
    print(response_delete_host.json())
    manager.publish()
    manager.logout()
    assert response_delete_host.status_code == 200
