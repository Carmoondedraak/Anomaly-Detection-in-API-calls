import datetime
import decorator
import json
import requests
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from escherauth import EscherRequestsAuth


# pylint: disable=missing-docstring, too-many-arguments, invalid-name

@decorator.decorator
def verify(func, *args, **kwargs):
    res = func(*args, **kwargs)

    if res.ok is False:
        try:
            raise Exception(res.json())
            raise Exception(res.json())
        except ValueError:
            raise Exception("Error code was {} but there was no bodjson. Text was '{}'".format(
                res.status_code, res.text))

    if res.status_code != 204:
        try:
            return res.json()
        except ValueError:
            raise Exception("Status code was {} but there was no json. Text was '{}'".format(
                res.status_code, res.text))
    return 'OK'


def wait_for_healthy_cluster(host):
    client_instance = PortshiftClient(host)

    times = 0
    while True:
        if client_instance.is_healthy():
            return client_instance

        if times > 300:
            raise Exception("Cluster is not healthy")

        times += 1
        print('Waiting for cluster to be healthy {} ...'.format(times))
        time.sleep(1)

    return client_instance


def scn_connect(config):
    print(f"Establish a connection with SCN cluster {config['SCN_HOST']}")
    client = wait_for_healthy_cluster(config['SCN_HOST'])
    if not config['SCN_ACCESS_KEY']:
        client.login(config['SCN_USERNAME'], config['SCN_PASSWORD'])
        accounts = client.list_accounts('demo user')
        account_id = accounts[0]["id"]
        client.assign_account(account_id)
    else:
        client.escher_login(scope=config['SCN_ESCHER_SCOPE'], access_key=config['SCN_ACCESS_KEY'],
                            secret_key=config['SCN_SECRET_KEY'])
    return client


def format_key_value_class_list(items):
    formatted_items = []
    if items:
        for key, value in items.items():
            formatted_item = {
                'key': key,
                'value': value
            }

            formatted_items.append(formatted_item)

    return formatted_items if formatted_items else None


class AppUserRuleAppPart:
    def __init__(self, workload_rule_type, names=None, types=None, labels_dict=None, highestVulnerabilityAllowed=None,
                 on_vulnerability_violation=None, psp_profile_id=None, on_psp_violation=None):
        self.workload_rule_type = workload_rule_type
        self.names = names
        self.types = types
        self.labels_dict = labels_dict
        self.highestVulnerabilityAllowed = highestVulnerabilityAllowed
        self.on_vulnerability_violation = on_vulnerability_violation
        self.psp_profile_id = psp_profile_id
        self.on_psp_violation = on_psp_violation

    def get_formatted_dict(self):
        formatted_dict = {
            "workloadRuleType": self.workload_rule_type,
            "names": self.names,
            "types": self.types,
            "podValidation": {
                "vulnerability": {
                    "highestVulnerabilityAllowed": self.highestVulnerabilityAllowed,
                    "onViolationAction": self.on_vulnerability_violation
                } if self.highestVulnerabilityAllowed else None,
                "podSecurityPolicy": {
                    "podSecurityPolicyId": self.psp_profile_id,
                    "onViolationAction": self.on_psp_violation
                } if self.psp_profile_id else None,
                "apiSecurityPolicy": None
            } if self.highestVulnerabilityAllowed or self.psp_profile_id else None,
            "labels": format_key_value_class_list(self.labels_dict) if self.labels_dict else None
        }

        return {key: value for key, value in list(formatted_dict.items()) if value is not None}


class AppUserRuleEnvPart:
    def __init__(self, environment_rule_type, names=None, risks=None):
        self.environment_rule_type = environment_rule_type
        self.names = names
        self.risks = risks

    def get_formatted_dict(self):
        formatted_dict = {
            "environmentRuleType": self.environment_rule_type,
            "names": self.names if self.names else None,
            "risks": self.risks if self.risks else None
        }

        return {key: value for key, value in list(formatted_dict.items()) if value is not None}


class AppUserRule:
    def __init__(self, name, app_part_type, env_part_type, type="ALLOW", status="ENABLED", id=None, group_name=None,
                 origin='USER'):
        self.name = name
        self.action = type
        self.status = status
        self.app_part_type = app_part_type
        self.env_part_type = env_part_type
        self.id = id
        self.groupName = group_name
        self.ruleOrigin = origin
        self.ruleType = "ViolationRuleType"

    def get_formatted_dict(self):
        if self.action is None:
            return {
                "name": self.name,
                "ruleTypeProperties": {
                    "ruleType": self.ruleType
                },
                "status": self.status,
                "app": self.app_part_type.get_formatted_dict(),
                "environment": self.env_part_type.get_formatted_dict(),
                "groupName": self.groupName,
                "id": self.id,
                "ruleOrigin": self.ruleOrigin
            }
        return {
            "name": self.name,
            "ruleTypeProperties": {
                "ruleType": self.ruleType,
                "action": self.action},
            "status": self.status,
            "app": self.app_part_type.get_formatted_dict(),
            "environment": self.env_part_type.get_formatted_dict(),
            "groupName": self.groupName,
            "id": self.id,
            "ruleOrigin": self.ruleOrigin
        }


class ConnectionUserRuleEndpointPart:
    def __init__(self, connection_rule_part_type, names=None, environments=None, types=None, labels_dict=None,
                 networks=None, fqdnAddresses=None, clusterId=None, services=None, vulnerabilitySeverityLevel=None,
                 brokers=None, apiSecurityProfile=None):
        self.connection_rule_part_type = connection_rule_part_type
        self.names = names
        self.environments = environments
        self.types = types
        self.labels_dict = labels_dict
        self.networks = networks
        self.fqdnAddresses = fqdnAddresses
        self.clusterId = clusterId
        self.services = services
        self.vulnerabilitySeverityLevel = vulnerabilitySeverityLevel
        self.brokers = brokers
        self.apiSecurityProfile = apiSecurityProfile

    def should_return_api_security_profile(self, key, connection_rule_part_type):
        if key != 'apiSecurityProfile':
            return False
        if connection_rule_part_type != 'PodNameConnectionRulePart' and connection_rule_part_type != 'PodLablesConnectionRulePart' and connection_rule_part_type != 'PodAnyConnectionRulePart':
            return False
        return True

    def get_formatted_dict(self):
        formatted_dict = {
            "connectionRulePartType": self.connection_rule_part_type,
            "names": self.names,
            "environments": self.environments,
            "types": self.types,
            "labels": format_key_value_class_list(self.labels_dict) if self.labels_dict else None,
            "networks": self.networks,
            "fqdnAddresses": self.fqdnAddresses,
            "services": self.services,
            "vulnerabilitySeverityLevel": self.vulnerabilitySeverityLevel,
            "apiSecurityProfile": self.apiSecurityProfile,
            "brokers": self.brokers,
            "clusterId": self.clusterId}

        return {key: value for key, value in list(formatted_dict.items()) if
                value is not None or self.should_return_api_security_profile(key, self.connection_rule_part_type)}


class ConnectionUserRule:
    def __init__(self, name, source_part_type, destination_part_type, action="ALLOW", status="ENABLED", id=None,
                 group_name=None, layer7_settings=None):
        self.name = name
        self.action = action
        self.status = status
        self.source_part_type = source_part_type
        self.destination_part_type = destination_part_type
        self.id = id
        self.groupName = group_name
        self.layer7_settings = layer7_settings

    def get_formatted_dict(self):
        data = {
            "name": self.name,
            "action": self.action,
            "status": self.status,
            "source": self.source_part_type.get_formatted_dict(),
            "destination": self.destination_part_type.get_formatted_dict(),
            "groupName": self.groupName,
            "id": self.id
        }

        if self.layer7_settings is not None:
            data["layer7Settings"] = self.layer7_settings.get_formatted_dict()
        return data


class HttpLayer7Part:
    def __init__(self, methods, paths, isIntercept=False, layer7_Protocol="HttpLayer7Part"):
        self.layer7Protocol = layer7_Protocol
        self.methods = methods
        self.paths = paths
        self.isIntercept = isIntercept

    def get_formatted_dict(self):
        return {
            "layer7Protocol": self.layer7Protocol,
            "methods": self.methods,
            "paths": self.paths,
            "isIntercept": self.isIntercept
        }


class KafkaLayer7Part:
    def __init__(self, topics, actions, layer7_Protocol="KafkaLayerPart"):
        self.layer7Protocol = layer7_Protocol
        self.topics = topics
        self.actions = actions

    def get_formatted_dict(self):
        return {
            "layer7Protocol": self.layer7Protocol,
            "topics": self.topics,
            "actions": self.actions
        }


class KubernetesEnvironmentPart:
    def __init__(self, cluster_id, namespace_names, namespace_labels=None, id=None):
        self.cluster_id = cluster_id
        self.namespace_names = namespace_names
        self.namespace_labels = namespace_labels
        self.id = id

    def get_formatted_dict(self):
        return {
            "kubernetesCluster": self.cluster_id,
            "namespaces": self.namespace_names,
            "namespaceLabels": format_key_value_class_list(self.namespace_labels),
            "id": self.id
        }


class AwsEnvironmentPart:
    def __init__(self, aws_account_id, region_id, vpc_id, tags=None, id=None):
        self.aws_account_id = aws_account_id
        self.vpc_id = vpc_id
        self.region_id = region_id
        self.tags = tags
        self.id = id

    def get_formatted_dict(self):
        return {
            "vpc": {
                "awsAccountId": self.aws_account_id,
                "regionId": self.region_id,
                "vpcId": self.vpc_id
            },
            "tags": format_key_value_class_list(self.tags),
            "id": self.id
        }


class PortshiftClient(object):
    def __init__(self, url):
        self._url = url
        self._session = requests.Session()
        self._session.headers.update({'content-type': 'application/json'})

    def _build_url(self, url):
        return self._url + '/api' + url

    def _account_url(self, url):
        return self._build_url(url)

    @staticmethod
    def convert_dict_to_key_value_list(dict_to_convert):
        converted_list = []
        if dict_to_convert is not None:
            for k, v in list(dict_to_convert.items()):
                converted_list.append(dict(key=k, value=v))

        return converted_list

    def setup_test_account(self, user_email, password, admin_password, account_name="user", user_name="Awesome User"):
        try:
            self.login(user_email, password)
        except Exception:
            admin_user = "blabla@mailinator.com"
            try:
                self.login(admin_user, admin_password)
            except Exception:
                # no admin user - create admin account
                self.create_account(admin_user, "John Doe", "admin", "PORTSHIFT_ADMIN")
                self.login(admin_user, admin_password)
            finally:
                self.accept_eula()

            # no account user - create user account
            self.create_account(user_email, user_name, account_name, "ACCOUNT_ADMIN", user_desc=None, account_desc=None,
                                account_status='ENABLED', permissions_mode='NORMAL', account_tier='CONNECT',
                                api_security='ENABLED')
            self.login(user_email, password)
        finally:
            self.accept_eula()

            service_user_exists = False
            users = self.list_users()
            for user in users:
                if user["role"] == 'SERVICE':
                    service_user_exists = True

            if not service_user_exists:
                self.add_user('api tests service user', 'SERVICE')

    @verify
    def add_user(self, full_name, role='ACCOUNT_ADMIN', email=None, description=None):
        data = {'fullName': full_name,
                'description': description,
                'status': 'ENABLED',
                'role': role
                }

        if email is not None:
            data['email'] = email

        return self._session.post(self._build_url('/users'), data=json.dumps(data))

    @verify
    def update_user(self, user_id, full_name, description, status):
        data = {
            'fullName': full_name,
            'description': description,
            'status': status
        }

        return self._session.put(self._build_url('/users/{}'.format(user_id)), data=json.dumps(data))

    @verify
    def delete_user(self, user_id):
        return self._session.delete(self._build_url('/users/{}'.format(user_id)))

    @verify
    def list_users(self):
        return self._session.get(self._build_url('/users'))

    @verify
    def get_user_access_tokens(self, user_id):
        return self._session.get(self._build_url('/users/{}/accessTokens'.format(user_id)))

    @verify
    def get_params(self):
        return self._session.get(self._build_url('/params'))

    @verify
    def get_psps(self):
        return self._session.get(self._build_url('/podSecurityPolicyProfiles'))

    @verify
    def add_psp(self, profileJsonString):
        return self._session.post(self._account_url('/podSecurityPolicyProfiles'),
                                  data=profileJsonString)

    @verify
    def add_crankshaft_data(self, account_id):
        return self._session.post(self._build_url('/admin/accounts/' + account_id +
                                                  '/crankshaft'))

    @verify
    def list_internal_catalogs_apis(self):
        return self._session.get(self._build_url('/apiSecurity/internalCatalog'))

    @verify
    def list_external_catalogs_apis(self):
        return self._session.get(self._build_url('/apiSecurity/externalCatalog'))

    @verify
    def fetch_internal_api_specs_by_id(self, catalogue_id):
        return self._session.get(
            self._build_url('/apiSecurity/internalCatalog/{}'.format(catalogue_id)))

    @verify
    def fetch_external_api_specs_by_id(self, catalogue_id):
        return self._session.get(
            self._build_url('/apiSecurity/externalCatalog/{}'.format(catalogue_id)))

    @verify
    def list_dashboard_clusters(self):
        return self._session.get(self._build_url('/dashboard/clusters'))

    @verify
    def list_connection_rules(self):
        return self._session.get(self._build_url('/connectionsPolicy'))

    @verify
    def upload_api_spec(self, id, data):
        return self._session.put(self._build_url('/apiSecurity/openApiSpecs/{}'.format(id)),
                                 data=json.dumps(data))

    @verify
    def fetch_open_api_specs(self, catalogue_id):
        return self._session.get(
            self._build_url('/apiSecurity/openApiSpecs/{}'.format(catalogue_id)))

    @verify
    def create_token(self, token):
        return self._session.post(self._build_url('/tokens'), data=json.dumps(token))

    @verify
    def list_tokens(self):
        return self._session.get(self._build_url('/tokens'))

    @verify
    def delete_token(self, id):
        return self._session.delete(self._build_url(f'/tokens/{id}'))

    @verify
    def add_seccomp_profile(self, profileJsonString):
        return self._session.post(self._account_url('/seccompProfiles'),
                                  data=profileJsonString)

    def escher_login(self, scope, access_key, secret_key):
        """Initialize session mandatory"""

        r = urllib.parse.urlparse(self._url)
        # TODO: automatically add https scheme and 443 port if no present
        # if r.scheme not in ['https']:
        #     r = r._replace(scheme='https')
        self._base_url = urllib.parse.urlunparse(r)
        try:
            self._escher_key = access_key
            self._escher_secret = secret_key
            self._escher_scope = scope
        except Exception as e:
            raise Exception(f'Unable to set Escher crendentials: {e}')
        # logger.debug(f"ManagementClient - Escher Scope: {self._escher_scope}, Escher Key: {self._escher_key}, Escher Secret: {self._escher_secret[:5]}...")

        self._escher_client = {'api_key': self._escher_key, 'api_secret': self._escher_secret}

        self._session.headers['host'] = r.netloc.split(':')[0]
        options = {}
        self._session.auth = EscherRequestsAuth(self._escher_scope, options, self._escher_client)
        self._session.verify = False

    @verify
    def login(self, email, password):
        headers = {
            'accept': 'application/json',
            'authorization': 'Basic MG9hYm5hcW94d0tXU2c5WFoxZDY6QXVJNGw2SGhOa2lxTWVzQ0E1OXYzdEFwUzJYaHF1b2hmZElhYWM0bw==',
            'content-type': 'application/x-www-form-urlencoded',
        }

        data = {
            'grant_type': 'password',
            'username': email,
            'password': password,
            'scope': 'openid'
        }

        response = requests.post('https://k8sec-dev.oktapreview.com/oauth2/default/v1/token', headers=headers,
                                 data=data)

        j = response.json()
        accessToken = j['access_token']
        return self._session.post(self._build_url('/login'), headers={'token': accessToken})

    @verify
    def me(self):
        return self._session.get(self._build_url('/me'))

    def logout(self):
        return self._session.post(self._build_url('/logout'))

    @verify
    def delete_kubernetes_cluster(self, id):
        return self._session.delete(self._account_url(f'/kubernetesClusters/{id}'))

    @verify
    def list_kubernetes_clusters(self):
        return self._session.get(self._account_url('/kubernetesClusters'))

    @verify
    def update_kubernetes_clusters(self, cluster_id, data):
        return self._session.put(self._account_url('/kubernetesClusters/{}'.format(cluster_id)), data=json.dumps(data))

    @verify
    def fuzz_api(self, catalogue_id):
        return self._session.post(self._account_url('/apiSecurity/internalCatalog/{}/fuzzingScan'.format(catalogue_id)))

    @verify
    def add_kubernetes_cluster(self, name, type, ci_validation='false', preserve_original_source_ip=False,
                               token_injection_enabled=False,
                               tracing_support_enabled=False,
                               connection_control_enabled=True):
        if not connection_control_enabled:
            preserve_original_source_ip = False
            
        return self._session.post(self._account_url('/kubernetesClusters'),
                                  data=json.dumps({"name": name, "clusterPodDefinitionSource": type,
                                                   "ciImageValidation": ci_validation,
                                                   "enableConnectionsControl": connection_control_enabled,
                                                   "tokenInjectionEnabled": token_injection_enabled,
                                                   "proxyConfiguration": {
                                                       "enableProxy": False
                                                   },
                                                   "installTracingSupport": tracing_support_enabled,
                                                   "installEnvoyTracingSupport": tracing_support_enabled,
                                                   "supportExternalTraceSource": tracing_support_enabled,
                                                   "preserveOriginalSourceIp": preserve_original_source_ip}))


    @verify
    def add_expansion(self, name, labels_dict, workload_addresses, network_protocols, cluster_id, namespace_id):
        if len(workload_addresses) != len(network_protocols):
            raise Exception("addresses and network protocols should be in the same size")
        workload_addresses_api = []
        for address, protocol in zip(workload_addresses, network_protocols):
            workload_addresses_api.append({"address": address,
                                           "networkProtocol": protocol})

        return self._session.post(self._account_url('/expansions'),
                                  data=json.dumps({
                                      "name": name,
                                      "labels": self.convert_dict_to_key_value_list(labels_dict),
                                      "workloadAddresses": workload_addresses_api,
                                      "clusterId": cluster_id,
                                      "namespaceId": namespace_id}))

    @verify
    def add_splunk_event_forwarding_integration(self, name, port=8088, url="some_url", token="some_token",
                                                events_to_forward=["NOTIFICATION", "ADMINISTRATIVE"]):
        return self._session.post(self._account_url('/settings/integrations/eventForwarding'), data=json.dumps({
            "eventsForwardingDetailsType": "SplunkEventsForwardingDetails",
            "isCloud": True,
            "port": port,
            "name": name,
            "url": url,
            "token": token,
            "eventsToForward": events_to_forward
        }))

    @verify
    def edit_splunk_event_forwarding_integration(self, id, new_name, port=8088, url="some_url", token="some_token",
                                                 events_to_forward=["NOTIFICATION", "ADMINISTRATIVE"]):
        return self._session.put(self._account_url('/settings/integrations/eventForwarding/{}'.format(id)),
                                 data=json.dumps({
                                     "eventsForwardingDetailsType": "SplunkEventsForwardingDetails",
                                     "isCloud": True,
                                     "port": port,
                                     "name": new_name,
                                     "url": url,
                                     "token": token,
                                     "eventsToForward": events_to_forward
                                 }))

    @verify
    def add_ops_genie_event_forwarding_integration(self, name, token="some_token",
                                                   events_to_forward=["NOTIFICATION", "ADMINISTRATIVE"]):
        return self._session.post(self._account_url('/settings/integrations/eventForwarding'), data=json.dumps({
            "eventsForwardingDetailsType": "OpsGenieEventsForwardingDetails",
            "name": name,
            "token": token,
            "eventsToForward": events_to_forward
        }))

    @verify
    def edit_ops_genie_event_forwarding_integration(self, id, new_name, url="some_url", token="some_token",
                                                    events_to_forward=["NOTIFICATION", "ADMINISTRATIVE"]):
        return self._session.put(self._account_url('/settings/integrations/eventForwarding/{}'.format(id)),
                                 data=json.dumps({
                                     "eventsForwardingDetailsType": "OpsGenieEventsForwardingDetails",
                                     "name": new_name,
                                     "url": url,
                                     "token": token,
                                     "eventsToForward": events_to_forward
                                 }))

    @verify
    def add_slack_event_forwarding_integration(self, name, url="some_url",
                                               events_to_forward=["NOTIFICATION", "ADMINISTRATIVE"]):
        return self._session.post(self._account_url('/settings/integrations/eventForwarding'), data=json.dumps({
            "eventsForwardingDetailsType": "SlackEventsForwardingDetails",
            "name": name,
            "url": url,
            "eventsToForward": events_to_forward
        }))

    @verify
    def add_slack_vul_event_forwarding_integration(self, name, url="some_url",
                                                   events_to_forward=["NOTIFICATION", "VULNERABILITY"],
                                                   vulnerability_severity=None):
        return self._session.post(self._account_url('/settings/integrations/eventForwarding'), data=json.dumps({
            "eventsForwardingDetailsType": "SlackVulnerabilityEventsForwardingDetails",
            "name": name,
            "url": url,
            "eventsToForward": events_to_forward,
            "vulnerabilitySeverity": vulnerability_severity
        }))

    @verify
    def edit_slack_event_forwarding_integration(self, id, new_name, url="some_url",
                                                events_to_forward=["NOTIFICATION", "ADMINISTRATIVE"]):
        return self._session.put(self._account_url('/settings/integrations/eventForwarding/{}'.format(id)),
                                 data=json.dumps({
                                     "eventsForwardingDetailsType": "SlackEventsForwardingDetails",
                                     "name": new_name,
                                     "url": url,
                                     "eventsToForward": events_to_forward
                                 }))

    @verify
    def delete_event_forwarding_integration(self, id):
        return self._session.delete(self._account_url('/settings/integrations/eventForwarding/{}'.format(id)))

    @verify
    def edit_agent_status(self, cluster_id, status):
        return self._session.post(self._account_url('/admin/agents/updateState/{}'.format(cluster_id)),
                                  data=json.dumps(status))

    @verify
    def edit_kubernetes_cluster(self, cluster_id, name=None, type=None):
        data = {}
        if name is not None:
            data["name"] = name
        if type is not None:
            data["clusterPodDefinitionSource"] = type
        data["enableConnectionsControl"] = True

        return self._session.put(self._account_url('/kubernetesClusters/{}'.format(cluster_id)),
                                 data=json.dumps(data))

    @verify
    def delete_kubernetes_cluster(self, cluster_id):
        return self._session.delete(self._account_url('/kubernetesClusters/{}'.format(cluster_id)))

    def download_yaml(self, cluster_id):
        res = self._session.get(
            self._account_url('/kubernetesClusters/{}/portshift_bundle.yml'.format(cluster_id)))
        res.raise_for_status()
        return res.text

    def download_installer(self, cluster_id):
        res = self._session.get(
            self._account_url('/kubernetesClusters/{}/download_bundle'.format(cluster_id)), stream=True)
        res.raise_for_status()
        return res.raw

    @verify
    def list_namespaces(self, cluster_id):
        return self._session.get(
            self._account_url('/kubernetesClusters/{}/namespaces'.format(cluster_id)))

    @verify
    def list_pod_definitions(self, filters=None):
        url = '/podDefinitions'

        if filters:
            url = "{}?{}".format(url, urllib.parse.urlencode(filters))

        return self._session.get(self._account_url(url))

    @verify
    def add_pod_definition(self, name, source, kind, images, labels_dict, cluster_id):
        containers = []
        if images is not None:
            for image in images:
                containers.append({"image": image})

        data = {
            "name": name,
            "kind": kind,
            "podDefinitionSource": source,
            "containers": containers,
            "labels": self.convert_dict_to_key_value_list(labels_dict),
            "clusterId": cluster_id
        }

        return self._session.post(self._account_url('/podDefinitions'), data=json.dumps(data))

    @verify
    def edit_pod_definition(self, pod_id, name, source, kind, images, labels_dict, cluster_id):
        containers = []
        if images is not None:
            for image in images:
                containers.append({"image": image})

        data = {
            "name": name,
            "kind": kind,
            "podDefinitionSource": source,
            "containers": containers,
            "labels": self.convert_dict_to_key_value_list(labels_dict),
            "clusterId": cluster_id
        }

        return self._session.put(self._account_url('/podDefinitions/{}'.format(pod_id)), data=json.dumps(data))

    @verify
    def delete_pod_definition(self, pod_id):
        return self._session.delete(self._account_url('/podDefinitions/{}'.format(pod_id)))

    @verify
    def add_role(self, name, arn):
        return self._session.post(self._account_url('/aws/roles'),
                                  data=json.dumps({'arn': arn, 'name': name, 'description': 'the AWS role'}))

    @verify
    def learn_api(self, catalogue_id, clusterId, learningMins):
        return self._session.post(self._account_url('/apiSecurity/openApiSpecs/{}/reconstructedSpec/learn'
                                                    .format(catalogue_id)), data=json.dumps({'clusterId': clusterId, "learningDuration": f"PT{learningMins}M"}))

    @verify
    def check_learn_status(self, catalog_id):
        return self._session.get(
            self._account_url('/apiSecurity/openApiSpecs/{}/reconstructedSpec/status'.format(catalog_id)))

    @verify
    def review_items(self, catalog_id):
        return self._session.get(
            self._account_url('/apiSecurity/openApiSpecs/{}/reconstructedSpec/review'.format(catalog_id)))

    @verify
    def approve_review(self, catalogue_id, data):
        return self._session.post(self._account_url('/apiSecurity/openApiSpecs/{}/reconstructedSpec/review/approve'
                                                    .format(catalogue_id)), data=json.dumps(data))
    @verify
    def fetch_reconstructed_spec(self, catalog_id):
        return self._session.get(
            self._account_url('/apiSecurity/openApiSpecs/{}/reconstructedSpecJson'.format(catalog_id)))

    @verify
    def update_role(self, role_id, name, description):
        return self._session.put(self._account_url('/aws/roles/{}'.format(role_id)),
                                 data=json.dumps({'name': name, 'description': description}))

    @verify
    def list_roles(self):
        return self._session.get(self._account_url('/aws/roles'))

    @verify
    def list_aws_accounts(self):
        return self._session.get(self._account_url('/aws/accounts'))

    @verify
    def list_aws_regions(self, account_id):
        return self._session.get(self._account_url('/aws/{}/regions'.format(account_id)))

    @verify
    def list_vpcs(self, account_id, region_id):
        return self._session.get(self._account_url('/aws/{}/{}/vpcs'.format(account_id, region_id)))

    @verify
    def list_subnets(self, account_id, region_id):
        return self._session.get(self._account_url('/aws/{}/{}/subnets'.format(account_id, region_id)))

    @verify
    def list_instance_tags(self):
        return self._session.get(self._account_url('/aws/tags'))

    @verify
    def add_dockerfile_scan_result(self, image_hash, title, account_id, description, severity, test):
        obj = {
            "imageHash": image_hash,
            "title": title,
            "description": description,
            "severity": severity,
            "test": test
        }

        return self._session.post(
            self._account_url('/admin/accounts/' + account_id + '/images/dockerfileScanResults'),
            data=json.dumps(obj))

    @verify
    def list_environments(self):
        return self._session.get(self._account_url('/environments'))

    @verify
    def add_environment(self, name, description=None, kubernetes_environments=None):
        return self._session.post(self._account_url('/environments'), data=json.dumps({
            "name": name,
            "description": description,
            "kubernetesEnvironments": [env.get_formatted_dict() for env in
                                       kubernetes_environments] if kubernetes_environments else None,
        }))

    @verify
    def edit_environment(self, id, name, risk, description=None, kubernetes_environments=None):
        return self._session.put(self._account_url('/environments/{}'.format(id)), data=json.dumps({
            "id": id,
            "name": name,
            "risk": risk,
            "description": description,
            "kubernetesEnvironments": [env.get_formatted_dict() for env in
                                       kubernetes_environments] if kubernetes_environments else None,
        }))

    @verify
    def delete_environments(self, id):
        return self._session.delete(self._account_url('/environments/{}'.format(id)))

    @verify
    def list_apps(self):
        return self._session.get(self._account_url('/apps'))

    @verify
    def get_app(self, app_id):
        return self._session.get(self._account_url('/apps/{}'.format(app_id)))

    @verify
    def add_app(self, name, app_type, exc, exc_path=None, proc_name=None, cwd=None, app_args=None, labels_dict=None):
        obj = {
            "name": name,
            "executable": exc,
            "executablePath": exc_path,
            "type": app_type,
            "processName": proc_name,
            "args": app_args,
            "cwd": cwd,
            "labels": self.convert_dict_to_key_value_list(labels_dict)
        }

        return self._session.post(self._account_url('/apps'), data=json.dumps(obj))

    @verify
    def edit_app(self, app_id, name, app_type, exc, exc_path, proc_name, cwd, app_args, labels_dict):
        obj = {
            "name": name,
            "executable": exc,
            "executablePath": exc_path,
            "type": app_type,
            "processName": proc_name,
            "args": app_args,
            "cwd": cwd,
            "labels": self.convert_dict_to_key_value_list(labels_dict)
        }

        return self._session.put(self._account_url('/apps/{}'.format(app_id)), data=json.dumps(obj))

    @verify
    def send_app_policy(self, default_rule_type="ALLOW_ALL", user_rules=[], unidentified_pods_rule_action="DETECT"):
        return self._session.put(self._account_url('/appsPolicy'), data=json.dumps({
            "defaultRule": default_rule_type,
            "unidentifiedPodsRule": {"action": unidentified_pods_rule_action},
            "userRules": [user_rule.get_formatted_dict() for user_rule in user_rules]
        }))

    @verify
    def send_app_policy_raw(self, data):
        return self._session.put(self._account_url('/appsPolicy'), data=json.dumps(data))

    @verify
    def list_apps_policy(self):
        return self._session.get(self._account_url('/appsPolicy'))

    @verify
    def delete_apps(self, app_ids):
        return self._session.post(self._account_url('/apps/delete'), data=json.dumps(app_ids))

    def is_healthy(self):
        try:
            res = self._session.get(self._build_url('/healthz'), timeout=1.0)
            res.raise_for_status()
            return True
        except Exception:
            return False

    @verify
    def list_agents(self, name):
        return self._session.get(self._account_url('/agents'),
                                 params={
                                     'hostName': name
                                 })

    @verify
    def edit_truncation_settings(self, truncate_days, truncate_is_enabled):
        return self._session.post(self._account_url('/truncation/workloads'), data=json.dumps({
            "truncateTimeInDays": truncate_days,
            "isTruncationEnabled": truncate_is_enabled
        }))

    @verify
    def get_truncation_settings(self, ):
        return self._session.get(self._account_url('/truncation/workloads'))

    @verify
    def query(self, start_time=datetime.datetime.utcnow() - datetime.timedelta(days=365),
              end_time=datetime.datetime.utcnow(),
              sort_key='startTime', sort_dir='ASC', only_defined_apps=False):
        ret = self._session.get(self._account_url('/appTelemetries'),
                                params={
                                    'startTime': start_time.isoformat() + 'Z',
                                    'endTime': end_time.isoformat() + 'Z',
                                    'sortKey': sort_key,
                                    'sortDir': sort_dir}).json()
        if only_defined_apps:
            ret = [x for x in ret if x['app']['name'] != 'N/A']

        return ret

    @verify
    def list_connections_policy(self):
        return self._session.get(self._account_url('/connectionsPolicy'))

    @verify
    def send_connections_policy(self, default_rule_type="ALLOW_ALL", default_rule_action="ALLOW", user_rules=[],
                                direct_pod_rule_action="DETECT"):
        return self._session.put(self._account_url('/connectionsPolicy'), data=json.dumps({
            "defaultRule": {
                "type": default_rule_type,
                "action": default_rule_action
            },
            "userRules": [user_rule.get_formatted_dict() for user_rule in user_rules],
            "directPodRule": {"action": direct_pod_rule_action}
        }))

    @verify
    def send_connections_policy_raw(self, default_rule_type="ALLOW_ALL", default_rule_action="ALLOW", user_rules=[],
                                    direct_pod_rule_action="DETECT"):
        return self._session.put(self._account_url('/connectionsPolicy'), data=json.dumps({
            "defaultRule": {
                "type": default_rule_type,
                "action": default_rule_action
            },
            "userRules": user_rules,
            "directPodRule": {"action": direct_pod_rule_action}
        }))

    @verify
    def accept_eula(self):
        return self._session.post(self._build_url('/users/acceptEula'))

    @verify
    def get_violations_dashboard(self):
        return self._session.get(self._account_url("/violationsDashboard"))

    @verify
    def get_operations_dashboard(self):
        return self._session.get(self._account_url("/operationsDashboard"))

    ###################### ADMIN APIs #######################

    @verify
    def update_account_settings(self, account_id, keep_alive, telemetries):
        return self._session.put(self._account_url('/admin/accounts/{}/settings'.format(account_id)), data=json.dumps({
            "agentSendStatusIntervalInSeconds": keep_alive,
            "agentSendTelemetriesIntervalInSeconds": telemetries
        }))

    @verify
    def get_account_settings(self, account_id):
        return self._session.get(self._account_url('/admin/accounts/{}/settings'.format(account_id)))

    @verify
    def create_kubernetes_api_policy(self, account_id, cluster_id):
        obj = {
        }
        return self._session.post(
            self._account_url('/admin/accounts/' + account_id + '/kubernetesApiPolicy/' + cluster_id),
            data=json.dumps(obj))

    @verify
    def list_accounts(self, name=None, sort_dir='ASC'):
        params = {
            'sortDir': sort_dir,
            'name': name,
        }

        return self._session.get(self._build_url('/admin/accounts'), params=params)

    @verify
    def cleanup_db(self):
        return self._session.put(self._build_url('/admin/cleanup'))

    @verify
    def get_all_states(self):
        return self._session.get(self._build_url('/admin/getAllStates'))

    @verify
    def get_account_policy_version(self, account_id):
        return self._session.get(self._build_url('/admin/accounts/policyVersion/{}'.format(account_id)))

    @verify
    def add_namespace(self, uid, name, labels, accountId, cluser_id=None):
        obj = {
            "uid": uid,
            "name": name,
            "labels": labels,
            "cluster_id": cluser_id
        }
        return self._session.post(
            self._account_url('/admin/accounts/' + accountId + '/namespaces'),
            data=json.dumps(obj))

    @verify
    def add_image(self, accountId, imageName, imageHash, scanned):
        obj = {
            "imageName": imageName,
            "imageHash": imageHash,
            "scanned": scanned
        }
        return self._session.post(
            self._account_url('/admin/accounts/' + accountId + '/images'),
            data=json.dumps(obj))

    @verify
    def add_permission(self, account_id, cluster_id, name, uid, scope, namespace, resource, resource_name, verbs,
                       groups):
        obj = {
            "cluster_id": cluster_id,
            "name": name,
            "uid": uid,
            "scope": scope,
            "namespace": namespace,
            "resource": resource,
            "resource_name": resource_name,
            "verbs": verbs,
            "groups": groups
        }
        return self._session.post(
            self._account_url('/admin/accounts/' + account_id + '/permission'),
            data=json.dumps(obj))

    @verify
    def add_permission_ownership(self, account_id, cluster_id, scope, permission_uid, owner_name, owner_namespace,
                                 owner_type):
        obj = {
            "cluster_id": cluster_id,
            "scope": scope,
            "permission_uid": permission_uid,
            "owner_name": owner_name,
            "owner_namespace": owner_namespace,
            "owner_type": owner_type
        }
        return self._session.post(
            self._account_url('/admin/accounts/' + account_id + '/permissionOwnership'),
            data=json.dumps(obj))

    @verify
    def add_cd(self, account_id, package_name, package_version, highest_risk_allowed, agent_id):
        obj = {
            "package_name": package_name,
            "package_version": package_version,
            "highest_risk_allowed": highest_risk_allowed,
            "agent_id": agent_id
        }
        return self._session.post(
            self._account_url('/admin/accounts/' + account_id + '/cd'),
            data=json.dumps(obj))

    @verify
    def add_registry(self, account_id, url, cluster_id):
        obj = {
            "url": url,
            "type": "OTHER",
            "clusterIds": [cluster_id]
        }
        return self._session.post(
            self._account_url('/registries'),
            data=json.dumps(obj))

    @verify
    def add_jfrog_private_registry(self, account_id, url, cluster_id, username, password, token):
        credentials = {
            "registryCredentialsType": "JfrogRegistryCredentials",
            "username": username,
            "password": password,
            "xrayToken": token
        }

        obj = {
            "url": url,
            "type": "JFROG",
            "clusterIds": [cluster_id],
            "credentials": credentials
        }
        return self._session.post(
            self._account_url('/registries'),
            data=json.dumps(obj))

    @verify
    def add_vulnerability(self, image_name, account_id, name, description, link, severity, found_in_package,
                          package_version, fix, cvss, cvss_score):
        obj = {
            "imageName": image_name,
            "name": name,
            "description": description,
            "link": link,
            "severity": severity,
            "foundInPackage": found_in_package,
            "packageVersion": package_version,
            "fix": fix,
            "cvss": cvss,
            "cvss_score": cvss_score
        }
        return self._session.post(
            self._account_url('/admin/accounts/' + account_id + '/images/vulnerabilities'),
            data=json.dumps(obj))

    @verify
    def add_topic(self, account_id, cluster_id, topic_name):
        obj = {
            "cluster_id": cluster_id,
            "topic_name": topic_name
        }
        return self._session.post(
            self._account_url('/admin/accounts/' + account_id + '/topics'),
            data=json.dumps(obj))

    @verify
    def add_token_injection_details(self, account_id):
        return self._session.post(self._build_url('/admin/accounts/' + account_id +
                                                  '/tokenInjection'))

    @verify
    def add_server_version(self, account_id, cluster_id, git_version, major, minor):
        obj = {
            "cluster_id": cluster_id,
            "git_version": git_version,
            "major": major,
            "minor": minor
        }
        return self._session.post(
            self._account_url('/admin/accounts/' + account_id + '/serverVersion'),
            data=json.dumps(obj))

    @verify
    def set_account_feature_dashboard_demo(self, account_id, is_dashboard_demo):
        return self._session.post(self._account_url('/admin/accounts/{}/features'.format(account_id)),
                                  data=json.dumps({"isDashboardDemo": is_dashboard_demo}))

    @verify
    def add_admin_user(self, full_name, role='PORTSHIFT_ADMIN', email=None, description=None):
        data = {'fullName': full_name,
                'description': description,
                'status': 'ENABLED',
                'role': role
                }

        if email is not None:
            data['email'] = email

        return self._session.post(self._build_url('/admin/users'), data=json.dumps(data))

    @verify
    def assign_account(self, account_id):
        data = {
            'assignedAccountId': account_id
        }
        return self._session.post(self._build_url('/admin/assignedAccount'), data=json.dumps(data))

    @verify
    def get_assigned_account(self):
        return self._session.get(self._build_url('/admin/assignedAccount'))

    @verify
    def create_account(self, email, user_name, account_name, role, user_desc=None, account_desc=None,
                       account_status='ENABLED', permissions_mode='NORMAL', account_tier='CONNECT',
                       api_security='DISABLED'):
        account = {"name": account_name,
                   "description": account_desc,
                   "permissionsMode": permissions_mode,
                   "status": account_status,
                   "accountTier": account_tier,
                   "apiSecurity": api_security}

        return self._session.post(self._build_url('/admin/accounts'), data=json.dumps(
            {'email': email,
             'fullName': user_name,
             'role': role,
             'description': user_desc,
             "status": account_status,
             'account': account}))

    @verify
    def update_account(self, account_id, name, description, status='ENABLED', permissions_mode='NORMAL',
                       account_tier='CONNECT'):
        data = {
            'name': name,
            'description': description,
            'permissionsMode': permissions_mode,
            'status': status,
            "accountTier": account_tier
        }

        return self._session.put(self._build_url('/admin/accounts/{}'.format(account_id)),
                                 data=json.dumps(data))

    @verify
    def delete_account(self, account_id):
        return self._session.delete(self._build_url('/admin/accounts/{}'.format(account_id)))

    @verify
    def update_policy_advisor(self):
        return self._session.post(self._build_url('/advisor/update'))

    @verify
    def add_telemetry(self, account_id, agent_id, start_time, end_time, pid, network,
                      instance_id, instance_name, aws_account, region, app_name, app_type, executable, executablePath,
                      env_name, env_risk, default_rule_violation=None):
        telemetry = {
            "agentId": agent_id,
            # "c6:8d:24:32:0e:cb:7f:d2:1c:55:44:d0:49:58:c8:21:96:9c:b4:a1:e9:79:75:5b:31:6b:ce:8c:72:32:da:21",
            "startTime": start_time,  # "2018-07-26T08:17:45.662Z",
            "endTime": end_time,  # "2018-07-26T08:17:45.662Z",
            "pid": pid,
            "instanceInfo": {
                "network": network,  # vpc-1234556
                "instanceId": instance_id,  # i-123143
                "cloudAccountId": aws_account,  # 6501567875
                "region": region,  # us-east-1
                "name": instance_name
            },
            "app": {
                "name": app_name,
                "type": app_type,
                "process": {
                    "executable": executable,
                    "executablePath": executablePath
                }
            },
            "environment": {
                "host": instance_id,
                "network": network,
                "name": env_name,
                "risk": env_risk,
            },
            "defaultRuleViolation": default_rule_violation,
        }

        return self._session.post(self._build_url('/admin/accounts/' + account_id +
                                                  '/appTelemetries'), data=json.dumps(telemetry))

    @verify
    def add_expansion_telemetry(self, account_id, expansion_uid, start_time, env_id, cluster_id):
        telemetry = {"startTime": start_time,
                     "expansion_uid": expansion_uid,
                     "env_id": env_id,
                     "cluster_id": cluster_id}
        return self._session.post(self._build_url('/admin/accounts/' + account_id +
                                                  '/expansionTelemetries'), data=json.dumps(telemetry))

    @verify
    def add_kubernetes_audit_log(self, account_id, cluster_id, resource_kind, resource_group, resource_name,
                                 namespace_name, user_name, user_namespace, user_group, kubernetes_action, rule_action,
                                 total):
        auditEvent = {"cluster_id": cluster_id,
                      "resource_kind": resource_kind,
                      "resource_group": resource_group,
                      "resource_name": resource_name,
                      "namespace_name": namespace_name,
                      "user_name": user_name,
                      "user_namespace": user_namespace,
                      "user_group": user_group,
                      "kubernetes_action": kubernetes_action,
                      "rule_action": rule_action,
                      "total": total}
        return self._session.post(self._build_url('/admin/accounts/' + account_id +
                                                  '/kubernetesAuditEvents'), data=json.dumps(auditEvent))

    @verify
    def add_pod_telemetry(self, account_id, start_time, end_time, pod_uid,
                          pod_template_uid, deployment_kind, node, env_id, namespace, template_name, template_labels,
                          image_registry, image_name, image_version, jfrog_properties=None, default_rule_violation=None,
                          rule_id=None,
                          action=None,
                          pspInfo='STRICT',
                          podRuntimeInfo='{"runtimeLabels": [{"key": "team", "value": "R&D"}, {"key": "sensitivity", "value": "medium"}], "runtimeContainers": [{"image": {"repository": "registry.gitlab.com/portshift/portshift", "tag": "master-83484546"}}, {"image": {"repository": "registry.gitlab.com/portshift/portshift", "tag": "0.10.1.4"}}]}',
                          isIdentified=True, unidentified_pod_reasons=None, cluster_id=None, pod_status_reason=None,
                          violation_reason=None, psp_violation_reasons=None,
                          pod_template_diffs=None, is_public_facing=False, is_running_ssh=False,
                          pod_spec="{\"activeDeadlineSeconds\":null,\"affinity\":null,\"automountServiceAccountToken\":null,\"containers\":[{\"args\":null,\"command\":null,\"env\":null,\"envFrom\":null,\"image\":null,\"imagePullPolicy\":null,\"lifecycle\":null,\"livenessProbe\":null,\"name\":\"portshift\",\"ports\":null,\"readinessProbe\":null,\"resources\":null,\"securityContext\":{\"allowPrivilegeEscalation\":false,\"capabilities\":{\"add\":[\"NET_ADMIN\", \"SYS_TIME\"],\"drop\":[\"ALL\"]},\"privileged\":false,\"procMount\":\"Default\",\"readOnlyRootFilesystem\":true,\"runAsGroup\":4000,\"runAsNonRoot\":true,\"runAsUser\":1000,\"seLinuxOptions\":null},\"stdin\":null,\"stdinOnce\":null,\"terminationMessagePath\":null,\"terminationMessagePolicy\":null,\"tty\":null,\"volumeDevices\":null,\"volumeMounts\":null,\"workingDir\":null}],\"dnsConfig\":null,\"dnsPolicy\":null,\"hostAliases\":null,\"hostIPC\":false,\"hostNetwork\":false,\"hostPID\":false,\"hostname\":null,\"imagePullSecrets\":null,\"initContainers\":null,\"nodeName\":null,\"nodeSelector\":null,\"priority\":null,\"priorityClassName\":null,\"readinessGates\":null,\"restartPolicy\":null,\"runtimeClassName\":null,\"schedulerName\":null,\"securityContext\":{\"fsGroup\":2000,\"runAsGroup\":4000,\"runAsNonRoot\":true,\"runAsUser\":1000,\"seLinuxOptions\":null,\"supplementalGroups\":[0],\"sysctls\":null},\"serviceAccount\":null,\"serviceAccountName\":null,\"shareProcessNamespace\":true,\"subdomain\":null,\"terminationGracePeriodSeconds\":null,\"tolerations\":null,\"volumes\":[{\"name\":\"persistentVolumeClaim\"}, {\"name\":\"downwardAPI\"}, {\"name\":\"emptyDir\"}, {\"name\":\"secret\"}, {\"name\":\"projected\"}]}",
                          dockerfileScanSeverity=None, service_account_name=None):
        if service_account_name == None:
            service_account_name = template_name + " service account"
        telemetry = {"startTime": start_time,  # "2018-07-26T08:17:45.662Z",
                     "endTime": end_time,  # "2018-07-26T08:17:45.662Z",
                     "pod_uid": pod_uid,
                     "pod_template_uid": pod_template_uid,
                     "deploymentKind": deployment_kind,
                     "node": node,
                     "env_id": env_id,
                     "namespace": namespace,
                     "templates": [{
                         "name": template_name,
                         "uid": pod_template_uid
                     }],
                     "labels": template_labels,
                     "containers": [{"image": {"repository": image_registry + '/' + image_name,
                                               "tag": image_version,
                                               "dockerfileScanSeverity": dockerfileScanSeverity}}],
                     "podRuntimeInfo": podRuntimeInfo,
                     "pspInfo": pspInfo,
                     "jfrog_properties": jfrog_properties,
                     "rule_id": rule_id,
                     "action": action,
                     "defaultRuleViolation": default_rule_violation,
                     "isIdentified": isIdentified,
                     "unidentifiedPodReasons": unidentified_pod_reasons,
                     "cluster_id": cluster_id,
                     "pod_status_reason": pod_status_reason,
                     "violation_reason": violation_reason,
                     "psp_violation_reasons": psp_violation_reasons,
                     "podTemplateDiffs": pod_template_diffs,
                     "isPublicFacing": is_public_facing,
                     "isRunningSsh": is_running_ssh,
                     "podSpec": pod_spec,
                     "serviceAccountName": service_account_name}

        return self._session.post(self._build_url('/admin/accounts/' + account_id +
                                                  '/podTelemetries'), data=json.dumps(telemetry))

    @verify
    def add_connection(self, account_id, source_agent_id, source_pid, target_agent_id, target_pid,
                       start_time, end_time, source_ip='1.1.1.1', source_type=None,
                       target_type=None, default_rule_violation=None, violation_action=None, rule_id=None,
                       client_port=5555,
                       server_ip='2.2.2.2', server_port=2222, directPodIpConnectionRuleAction=None, server_fqdn=None,
                       layer_7_attributes=None, protocol='http'):
        connection = {
            "clientIp": source_ip,
            "clientPort": client_port,
            "serverIp": server_ip,
            "serverFqdn": server_fqdn,
            "serverPort": server_port,
            "sourceAgentId": source_agent_id,
            "targetAgentId": target_agent_id,
            "sourceType": source_type,
            "targetType": target_type,
            "startTime": start_time,
            "endTime": end_time,
            "defaultRuleViolation": default_rule_violation if default_rule_violation else "DENY_ALL",
            "violationAction": violation_action,
            "directPodIpConnectionRuleAction": directPodIpConnectionRuleAction,
            "ruleId": rule_id,
            "layer7Attributes": layer_7_attributes,
            "protocol": protocol
        }
        if source_pid is not None:
            connection['sourcePid'] = str(source_pid)
        if target_pid is not None:
            connection['targetPid'] = str(target_pid)

        return self._session.post(self._build_url('/admin/accounts/' + account_id +
                                                  '/connectionTelemetries'),
                                  data=json.dumps(connection))


if __name__ == "__main__":
    import IPython

    client = PortshiftClient(sys.argv[1])

    IPython.embed()
