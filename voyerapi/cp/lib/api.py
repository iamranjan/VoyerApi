import requests
import time
import re
from .utils import process_rule


class CheckpointAPIManager:
    """
    Top level class for managing calls to checkpoint management API
    """

    def __init__(self, hostname, username, password):
        requests.packages.urllib3.disable_warnings()
        self.base_url = "https://{}/{}".format(hostname, "web_api")
        self.username = username
        self.password = password
        self.session_timeout = "120"
        self.ready_only = "false"
        self.continue_last_session = "false"
        self.domain = ""
        self.session_comments = "scapi_manager_call"
        self.session_name = "scapi_manager"
        self.enter_last_published_session = "false"
        self.session_description = "scapi_manager"
        self.sid = None
        self.uid = None
        self.uuid_pattern = re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')

    def generate_header(self, sid=None):
        """
        generate headers
        :return:
        """
        if sid:
            return {
                'Content-Type': 'application/json',
                'X-chkp-sid': sid
            }
        else:
            return {
                'Content-Type': 'application/json'
            }

    def login(self):
        """
        Login to checkpoint management api and retrieve a token for session authentication etc
        :param base:
        :param payload:
        :return: response
        response.json() = {
        'uid': '3d87492d-da28-4c04-a524-6b819adfbda2',
        'sid': 'h9BjptS1A957F_hfxYaDN3HYc-XlJR5dUpo98DyZrQ0',
        'url': 'https://localhost:443/web_api',
        'session-timeout': 120,
        'last-login-was-at': {'posix': 1509152915467, 'iso-8601': '2017-10-27T21:08-0400'},
        'api-server-version': '1.1'
        }

        """
        body = {
            "user": self.username,
            "password": self.password,
            "continue-last-session": self.continue_last_session,
            "domain": self.domain,
            "enter-last-published-session": self.enter_last_published_session,
            "read-only": self.ready_only,
            "session-comments": self.session_comments,
            "session-description": self.session_description,
            "session-name": self.session_name,
            "session-timeout": self.session_timeout,
        }
        path = "{}/{}".format(self.base_url, "login")
        response = requests.post(path, json=body, headers=self.generate_header(), verify=False)

        try:
            print(response.json())
            self.sid = response.json()["sid"]
            self.uid = response.json()["uid"]
            return response
        except KeyError as e:
            print(response.json())
            response = requests.post(path, json=body, headers=self.generate_header(), verify=False)
            self.sid = response.json()["sid"]
            self.uid = response.json()["uid"]
            return response

    def logout(self, sid=None):
        """
        Logout of the checkpoint management api
        :return:
        """
        path = "{}/{}".format(self.base_url, "logout")

        if sid:
            self.discard(sid)
            return requests.post(path, json={}, headers=self.generate_header(sid), verify=False)
        else:
            self.discard(self.sid)
            return requests.post(path, json={}, headers=self.generate_header(self.sid), verify=False)

    def wait(self, task_id):
        """
        Poll a given task untill completed
        :param task_id:
        :return:
        """
        iterations = 0
        while True:
            response = self.show_task(task_id)
            task = response.json()['tasks'][0]
            print(response.status_code)
            print(task)
            iterations += 1
            if iterations > 100:
                return False
            if task:
                if task['progress-percentage'] == 100 and not task['status'] == 'failed':
                    print(task)
                    return True
                elif task['progress-percentage'] == 100 and task['status'] == 'failed':
                    print(task)
                    return False
            time.sleep(0.4)

    def show_task(self, task_id):
        """
        Check the state of a task
        :return:
        """
        body = {
            "task-id": task_id
        }
        path = "{}/{}".format(self.base_url, "show-task")
        if self.sid:
            return requests.post(path, json=body, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json=body, headers=self.generate_header(self.sid), verify=False)

    def cleanup(self):
        """
        Clean all remaining sessions incase atomic discard has failed
        :return: True
        """
        try:
            return self.discard_all_sessions()
        except Exception as e:
            return False

    def publish(self):
        """
        public/commit changes
        :return:
        """
        path = "{}/{}".format(self.base_url, "publish")
        if self.sid:
            response = requests.post(path, json={}, headers=self.generate_header(self.sid), verify=False)
            print("APIMANAGER:PUBLISH:RESPONSE:{}".format(response.json()))
            return response
        else:
            self.login()
            response = requests.post(path, json={}, headers=self.generate_header(self.sid), verify=False)
            print("APIMANAGER:PUBLISH:RESPONSE:{}".format(response.json()))
            return response

    def discard(self, uid=None):
        """
        discard uncommited changes
        :return:
        """
        if uid:
            body = {
                'uid': uid
            }
        else:
            body = {}
        path = "{}/{}".format(self.base_url, "discard")
        if self.sid:
            return requests.post(path, json=body, headers=self.generate_header(self.sid), verify=False)
        else:
            # self.login()
            return requests.post(path, json=body, headers=self.generate_header(self.sid), verify=False)

    def list_sessions(self):
        """
        List all active non-discarded sessions
        :return:
        """
        path = "{}/{}".format(self.base_url, "show-sessions")
        if self.sid:
            return requests.post(path, json={}, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json={}, headers=self.generate_header(self.sid), verify=False)

    def discard_all_sessions(self):
        """
        Cleanup all sessions, helpful when there are undiscarded sessions
        :return:
        """
        sessions = self.list_sessions()
        discarded_sessions = []
        for session in sessions.json()['objects']:
            print("APIMANAGER:DISCARDING:{}".format(session['uid']))
            discarded_sessions.append(session["uid"])
            print(self.discard(session["uid"]).json())
        return discarded_sessions

    def add_host(self, host):
        """
        Add host object
        :param host: dict:
          {
          "name":"Host-1",
          "ip-address":"10.1.3.21",
          "groups":"App-Hosts",
          "nat-settings":{"auto-rule":"True", "method":"static", "ip-address":"10.1.10.100"}
          }

        :return:
        """
        path = "{}/{}".format(self.base_url, "add-host")
        if self.sid:
            return requests.post(path, json=host, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json=host, headers=self.generate_header(self.sid), verify=False)

    def show_host(self, host):
        """
        Show host object
        :param host: dict:
          {
          "name":"Host-1"
          }

        :return:
        """
        path = "{}/{}".format(self.base_url, "show-host")
        if self.sid:
            return requests.post(path, json=host, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json=host, headers=self.generate_header(self.sid), verify=False)

    def delete_host(self, host):
        """
        Remove host. Not that if there is any association with a tag such as a group then you must
        also delete the tag to complete a full deletion of the host.
        :param host:
        {
          "name":"Host-1"
          }
        :return:
        """
        path = "{}/{}".format(self.base_url, "delete-host")
        if self.sid:
            return requests.post(path, json=host, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json=host, headers=self.generate_header(self.sid), verify=False)

    def add_network(self, network):
        """
        Add network object
        :param network:
         {
          "name":"Network-1",
          "subnet":"x.x.x.0",
          "subnet-mask":"255.255.255.0",
          }
        :return:
        """
        path = "{}/{}".format(self.base_url, "add-network")
        if self.sid:
            return requests.post(path, json=network, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json=network, headers=self.generate_header(self.sid), verify=False)

    def delete_network(self, network):
        """
        Delete network object
        :param network:
         {
          "name":"Network-1"
          }
        :return:
        """
        path = "{}/{}".format(self.base_url, "delete-network")
        if self.sid:
            return requests.post(path, json=network, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json=network, headers=self.generate_header(self.sid), verify=False)

    def list_group(self, group):
        """
        Fetch all groups matching group name
        :return:
        """
        path = "{}/{}".format(self.base_url, "show-group")
        if self.sid:
            return requests.post(path, json=group, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json=group, headers=self.generate_header(self.sid), verify=False)

    def add_group(self, group):
        """
        Add group object
        :param group:
        {
            "name":"App-Hosts"
        }
        :return:
        """
        path = "{}/{}".format(self.base_url, "add-group")
        if self.sid:
            return requests.post(path, json=group, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json=group, headers=self.generate_header(self.sid), verify=False)

    def add_tcp_service(self, service):
        """
        Add group object
        :param group:
        {
            "name":"kibana",
            "port": "5601"
        }
        :return:
        """
        path = "{}/{}".format(self.base_url, "add-service-tcp")
        if self.sid:
            return requests.post(path, json=service, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json=service, headers=self.generate_header(self.sid), verify=False)
    def show_tcp_service(self, service):
        """
        Add group object
        :param group:
        {
            "name":"kibana", (or uid)
        }
        :return:
        """

        if isinstance(service, str) and not re.search(self.uuid_pattern, service):
            service = {"name": service}
        elif isinstance(service, str) and re.search(self.uuid_pattern, service):
            service = {"uid": service}
        elif isinstance(service, dict):
            service = service
        path = "{}/{}".format(self.base_url, "show-service-tcp")
        if self.sid:
            return requests.post(path, json=service, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json=service, headers=self.generate_header(self.sid), verify=False)

    def delete_tcp_service(self, service):
        """
        Add group object
        :param group:
        {
            "name":"kibana",
            "port": "5601"
        }
        :return:
        """
        if isinstance(service, str):
            service = {"name": service}
        elif isinstance(service, dict):
            service = service
        path = "{}/{}".format(self.base_url, "delete-service-tcp")
        if self.sid:
            return requests.post(path, json=service, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json=service, headers=self.generate_header(self.sid), verify=False)

    def delete_group(self, group):
        """
        Delete group object
        :param group:
        :return:
        """
        path = "{}/{}".format(self.base_url, "delete-group")
        if self.sid:
            return requests.post(path, json=group, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json=group, headers=self.generate_header(self.sid), verify=False)

    def show_simple_gateways(self):
        """
        Delete group object
        :param:
        :return:
        """
        path = "{}/{}".format(self.base_url, "show-simple-gateways")
        if self.sid:
            return requests.post(path, json={}, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json={}, headers=self.generate_header(self.sid), verify=False)

    def show_simple_gateway(self, gateway):
        """
        Delete group object
        :param gateway:
        {
            "name":"App-Hosts"
        }
        :return:
        """
        path = "{}/{}".format(self.base_url, "show-simple-gateway")
        if self.sid:
            return requests.post(path, json=gateway, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json=gateway, headers=self.generate_header(self.sid), verify=False)

    def set_simple_gateway(self, gateway):
        """
        Update the simple gateway with the desired properties
        :param gateway:
        :return:
        """
        path = "{}/{}".format(self.base_url, "set-simple-gateway")
        if self.sid:
            return requests.post(path, json=gateway, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json=gateway, headers=self.generate_header(self.sid), verify=False)

    def add_simple_gateway(self, gateway):
        """
        Create simple gateway. This object represents an interface to interface connectivity pathway and requires
        the specification of interfaces for which is should use to establish connections?
        :param gateway:
        {
          "name" : "<username>",
          "ip-address" : ""
        }
                :return:
        """
        path = "{}/{}".format(self.base_url, "set-simple-gateway")
        if self.sid:
            return requests.post(path, json=gateway, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json=gateway, headers=self.generate_header(self.sid), verify=False)

    def add_access_layer(self, access_layer):
        """
        Add an access layer to the firewall. These appear to server the function of allowing contextualisation and
        grouping of policies to a given allow and then stacking these within a parent policy. The layer is comprised
        of a list of access rules which will be grouped/contextualised to the "layer".
        :param access_layer:
        {
            "name" : "Network"
            "applications-and-url-filtering":"True",
            "content-awareness":"True",
            "detect-using-x-forward-for":"True",
            "mobile-access":"False"
        }
        :return:
        """
        if isinstance(access_layer, str):
            layer = {"name": access_layer,
                     "applications-and-url-filtering": "True",
                     "content-awareness": "True",
                     "detect-using-x-forward-for": "True",
                     "mobile-access": "False"}
        elif isinstance(access_layer, dict):
            layer = access_layer

        path = "{}/{}".format(self.base_url, "add-access-layer")
        if self.sid:
            return requests.post(path, json=layer, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json=layer, headers=self.generate_header(self.sid), verify=False)

    def set_access_layer(self, access_layer):
        """
        Add an access layer to the firewall. These appear to server the function of allowing contextualisation and
        grouping of policies to a given allow and then stacking these within a parent policy. The layer is comprised
        of a list of access rules which will be grouped/contextualised to the "layer".
        :param access_layer:
        {
            "name" : "Network"
            "applications-and-url-filtering":"True",
            "content-awareness":"True",
            "detect-using-x-forward-for":"True",
            "mobile-access":"False"
        }
        :return:
        """
        if isinstance(access_layer, str):
            layer = {"name": access_layer,
                     "applications-and-url-filtering": "True",
                     "content-awareness": "True",
                     "detect-using-x-forward-for": "True",
                     "mobile-access": "False"}
        elif isinstance(access_layer, dict):
            layer = access_layer

        path = "{}/{}".format(self.base_url, "set-access-layer")
        if self.sid:
            return requests.post(path, json=layer, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json=layer, headers=self.generate_header(self.sid), verify=False)

    def delete_access_layer(self, access_layer):
        """
        Add an access layer to the firewall. These appear to server the function of allowing contextualisation and
        grouping of policies to a given allow and then stacking these within a parent policy. The layer is comprised
        of a list of access rules which will be grouped/contextualised to the "layer".
        :param access_layer:
        {
            "name" : "Network"
        }
        :return:
        """
        if isinstance(access_layer, str):
            layer = {"name": access_layer}
        elif isinstance(access_layer, dict):
            layer = access_layer
        path = "{}/{}".format(self.base_url, "delete-access-layer")
        if self.sid:
            response = requests.post(path, json=layer, headers=self.generate_header(self.sid), verify=False)
            print("APIMANAGER:DELETE_ACCESS_LAYER:RESPONSE:{}".format(response.json()))
            return response
        else:
            self.login()
            response = requests.post(path, json=layer, headers=self.generate_header(self.sid), verify=False)
            print("APIMANAGER:DELETE_ACCESS_LAYER:RESPONSE:{}".format(response.json()))
            return response

    def add_access_rule(self, access_rule):
        """
        Add access rule to a given layer, this is the core touch point of the interaction between the SCAPI and the
        checkpoint management API. The changes made in the editable CP panel will be utilising the functions
        here to carry out the required changes to the checkpoint FW.
        :param access_rule:
        {
            "name":"KIBANA",
            "layer":"Network",
            "position":"top",
            "source":"Any",
            "destination":["App-Hosts", "LB-VSes"],
            "service":["https", "http"],
            "action":"accept",
            "track":'log'
        }
        :return:
        """
        path = "{}/{}".format(self.base_url, "add-access-rule")
        if self.sid:
            return requests.post(path, json=access_rule, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json=access_rule, headers=self.generate_header(self.sid), verify=False)

    def add_nat_rule(self, nat_rule):
        """
        Add nat rule to a given layer, this is the core touchpoint to enable network connectivity
        :param access_rule:
        {
            "package-name":"PIPELINE",
            "position":"top",
            "original-source" : "Any",
            "original-service" : "9200",
            "original-destination" : "<public address>",
            "translated-destination	" : "<vsec internal>",
            "translated-service": "<same as origin-service>",
            "translated-source": "<vsec internal>"

        }
        :return:
        """
        path = "{}/{}".format(self.base_url, "add-nat-rule")
        if self.sid:
            return requests.post(path, json=nat_rule, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json=nat_rule, headers=self.generate_header(self.sid), verify=False)

    def delete_access_rule(self, access_rule):
        """
        delete access rule to a given layer, this is the core touch point of the interaction between the SCAPI and the
        checkpoint management API. The changes made in the editable CP panel will be utilising the functions
        here to carry out the required changes to the checkpoint FW.
        :param access_rule:
        {
            "name":"KIBANA",
            "layer": "Network",
        }
        :return:
        """
        path = "{}/{}".format(self.base_url, "delete-access-rule")
        if self.sid:
            return requests.post(path, json=access_rule, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json=access_rule, headers=self.generate_header(self.sid), verify=False)

    def set_access_rule(self, access_rule):
        """
        set/update access rule to a given layer, this is the core touch point of the interaction between the SCAPI and the
        checkpoint management API. The changes made in the editable CP panel will be utilising the functions
        here to carry out the required changes to the checkpoint FW.
        :param access_rule:
        {
            "name": "KIBANA",
            "layer": "Network",
        }
        :return:
        """
        path = "{}/{}".format(self.base_url, "set-access-rule")
        if self.sid:
            return requests.post(path, json=access_rule, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json=access_rule, headers=self.generate_header(self.sid), verify=False)

    def show_access_rule(self, access_rule):
        """
        set/update access rule to a given layer, this is the core touch point of the interaction between the SCAPI and the
        checkpoint management API. The changes made in the editable CP panel will be utilising the functions
        here to carry out the required changes to the checkpoint FW.
        :param access_rule:
        {
            "name": "KIBANA", or "uid"
            "layer": "Network",
        }
        :return:
        """
        path = "{}/{}".format(self.base_url, "show-access-rule")
        if self.sid:
            return requests.post(path, json=access_rule, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json=access_rule, headers=self.generate_header(self.sid), verify=False)

    def show_access_rulebase(self, rulebase):
        """
        set/update access rule to a given layer, this is the core touch point of the interaction between the SCAPI and the
        checkpoint management API. The changes made in the editable CP panel will be utilising the functions
        here to carry out the required changes to the checkpoint FW.
        :param rulebase:
        {
            "name": "PIPELINE Network", (layer-name)
            "offset": 0,
            "limit": 20,
            "details-level": "full",
            "use-object-dictionary": "true"
        }
        :return:
        """

        path = "{}/{}".format(self.base_url, "show-access-rulebase")
        if self.sid:
            return requests.post(path, json=rulebase, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json=rulebase, headers=self.generate_header(self.sid), verify=False)


    def show_rules(self, layer):
        """
        Highest level parent which manages the fetching and response of the access rules for a given layer. Manages
        both the show_access_rulebase (to fetch list) and the show_access_rule (specific rule) which produces a verbose
        list set containing the pertinent information for the rules such as the resolved services, designations and
        sources.
        Otherwise the rulebase on its own does not resolve the key objects and just returns them as object uid
        references.
        :return:
        """
        rules = []
        if isinstance(layer, str):
            layer_dict = {
                "name": layer,
                "offset": 0,
                "limit": 20,
                "details-level": "uid",
                "use-object-dictionary": "true"
            }
            rule_format = lambda x: {"uid": x["uid"], "layer": layer, "details-level": "full"}
        elif isinstance(layer, dict):
            layer_dict = layer
            rule_format = lambda x: {"uid": x["uid"], "layer": layer["name"], "details-level": "full"}
        rulebase = self.show_access_rulebase(layer_dict)
        if rulebase.status_code == 200:
            for rule in rulebase.json()['rulebase']:
                rule_object = {}
                rule_object['rule-number'] = rule['rule-number']
                response = self.show_access_rule(rule_format(rule)).json()
                rule_object['rule'] = process_rule(response)
                rules.append(rule_object)
            return rules
        else:
            raise Exception("Rulebase fetch request non-200")



    def delete_access_rulebase(self, rulebase):
        """
        With a given object name get rulebase items and delete matching. This enables removes of non-unique items
        via an iterative discovery process from the rulebase list to find UID's to delete with.
        :param rulebase:
        {
            "name": "<LAYER NAME>"
        }
        :return:
        """
        deleted_rules = []
        rulebase["offset"] = 0
        rulebase["limit"] = 30
        rulebase["details-level"] = "standard"
        rulebase["use-object-dictionary"] = "true"
        rulebase = self.show_access_rulebase(rulebase).json()

        if rulebase.get('rulebase'):
            num_rules = len(rulebase['rulebase'])
            for rule in rulebase['rulebase']:
                response = self.delete_access_rule({"uid": rule["uid"], "layer": rulebase["name"]})
                if response.status_code == 200:
                    deleted_rules.append(rule["uid"])

        if len(deleted_rules) != num_rules - 1:
            print("RULEBASE:DELETE:UNEXPECTED_NO:{}".format(deleted_rules))
            return deleted_rules
        else:
            return deleted_rules

    def add_package(self, package, gateways=None):
        """
        Add a policy package to the manager
        :param package:
        {
            "name": "PACKAGE_NAME",
            "access": "true",
            "threat-prevention": "true",
            "installation-targets": [ "GATEWAY_NAMES", .... ]
        }
        :return:
        """
        if isinstance(package, str) and gateways:
            package_dict = {
                "name": package,
                "access": "True",
                "threat-prevention": "true",
                "installation-targets": gateways
            }
        elif isinstance(package, dict) and gateways:
            package_dict = package
            package_dict["installation-targets"] = gateways

        elif isinstance(package, dict) and not gateways:
            package_dict = package

        path = "{}/{}".format(self.base_url, "add-package")
        if self.sid:
            return requests.post(path, json=package_dict, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json=package_dict, headers=self.generate_header(self.sid), verify=False)

    def set_package(self, package, layers):
        """
        Add a policy package to the manager
        :param package:
        {
            "name": "PACKAGE_NAME",
            "access": "true",
            "threat-prevention": "true",
            "installation-targets": [ "GATEWAY_NAMES", .... ]
        }
        :return:
        """
        if isinstance(package, str):
            package_dict = {
                "name": package,
                "access": "True",
                "access-layers": {
                    "value": layers,
                },
                "threat-prevention": "true",
                "installation-targets": "vsec"
            }
        elif isinstance(package, dict):
            package_dict = package

        path = "{}/{}".format(self.base_url, "set-package")
        if self.sid:
            return requests.post(path, json=package_dict, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json=package_dict, headers=self.generate_header(self.sid), verify=False)

    def delete_package(self, package, gateways=None):
        """
        delete a policy package to the manager
        :param package:
        {
            "name": "PACKAGE_NAME",
        }
        :return:
        """
        if isinstance(package, str) and gateways:
            package_dict = {
                "name": package,
            }
        elif isinstance(package, dict) and gateways:
            package_dict = package

        elif isinstance(package, dict) and not gateways:
            package_dict = package

        path = "{}/{}".format(self.base_url, "delete-package")
        if self.sid:
            return requests.post(path, json=package_dict, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json=package_dict, headers=self.generate_header(self.sid), verify=False)

    def show_package(self, package):
        """
        delete a policy package to the manager
        :param package:
        {
            "name": "PACKAGE_NAME",
        }
        :return:
        """
        if isinstance(package, str):
            package_dict = {
                "name": package,
            }
        elif isinstance(package, dict):
            package_dict = package

        path = "{}/{}".format(self.base_url, "show-package")
        if self.sid:
            return requests.post(path, json=package_dict, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json=package_dict, headers=self.generate_header(self.sid), verify=False)

    def verify_policy(self, policy):
        """
        Deploys a given policy on the firewall, like a commit/publish action
        :param policy:
        :param rulebase:
        {
            "policy-package": "POLICY_PACKAGE_NAME",
        }
        :return:
        """

        if isinstance(policy, str):
            policy_dict = {
                "policy-package": policy,
            }
        elif isinstance(policy, dict):
            policy_dict = policy
        else:
            return False
        path = "{}/{}".format(self.base_url, "verify-policy")
        if self.sid:
            response = requests.post(path, json=policy_dict, headers=self.generate_header(self.sid), verify=False)
            print(response.json())
            return self.wait(response.json()['task-id'])
        else:
            self.login()
            response = requests.post(path, json=policy_dict, headers=self.generate_header(self.sid), verify=False)
            print(response.json())
            return self.wait(response.json()['task-id'])

    def install_policy(self, policy, gateways):
        """
        Deploys a given policy on the firewall, like a commit/publish action
        :param rulebase:
        {
            "policy-package": "POLICY_PACKAGE_NAME",
            "access": "true",
            "threat-prevention": "true",
            "targets": [ "GATEWAY_NAMES" ]
        }
        :return:
        """

        if isinstance(policy, str) and gateways:
            policy_dict = {
                "policy-package": policy,
                "access": "True",
                "threat-prevention": "true",
                "targets": gateways
            }
        elif isinstance(policy, dict) and gateways:
            policy_dict = policy
            policy_dict["installation-targets"] = gateways

        elif isinstance(policy, dict) and not gateways:
            policy_dict = policy
        path = "{}/{}".format(self.base_url, "install-policy")
        if self.sid:
            return requests.post(path, json=policy_dict, headers=self.generate_header(self.sid), verify=False)
        else:
            self.login()
            return requests.post(path, json=policy_dict, headers=self.generate_header(self.sid), verify=False)
