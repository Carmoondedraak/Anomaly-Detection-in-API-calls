# coding=utf-8

import json
import os
import sys
import time
import traceback

import dotenv
import yaml

import portshift_cli
from sockshop_client import SockShopClient, SockShopLoadGen

config = {}
client = None


def load_config(envfile):
    global config
    print(f"Loading configuration from environment file {envfile}")

    config = dotenv.dotenv_values(envfile)


def scn_connect():
    global client
    client = portshift_cli.scn_connect(config)


def setup(clean=False):
    cluster_name = config['SCN_CLUSTER_NAME']

    if clean:
        # delete environment
        scn_envs = client.list_environments()
        for scn_env in scn_envs:
            print(f"{scn_env}")
            if scn_env['name'] == config['SCN_ENVIRONMENT']:
                client.delete_environments(scn_env['id'])
                break

        # delete cluster
        clusters = client.list_kubernetes_clusters()
        for cluster in clusters:
            if cluster['name'] == cluster_name:
                client.delete_kubernetes_cluster(cluster['id'])
        return

    try:

        connection_control_enabled = (config['WITH_ENVOY'] == "True")
        print(f"Adding k8s cluster {cluster_name}. Envoy enabled={connection_control_enabled}")
        cluster = client.add_kubernetes_cluster(cluster_name, 'KUBERNETES', preserve_original_source_ip=True,
                                                token_injection_enabled=connection_control_enabled, tracing_support_enabled=True, connection_control_enabled=connection_control_enabled)
    
    except Exception as e:
        print(e)
        clusters = client.list_kubernetes_clusters()
        for cluster in clusters:
            if cluster['name'] == cluster_name:  break

    k8s_env = portshift_cli.KubernetesEnvironmentPart(cluster["id"], namespace_names=[config['APP_NAMESPACE']])
    try:
        scn_env = client.add_environment(name=config['SCN_ENVIRONMENT'], kubernetes_environments=[k8s_env])
    except Exception as e:
        # Environment already exists
        scn_envs = client.list_environments()
        for scn_env in scn_envs:
            print(f"{scn_env}")
            if scn_env['name'] == config['SCN_ENVIRONMENT']:
                client.edit_environment(scn_env['id'], name=config['SCN_ENVIRONMENT'],
                                        kubernetes_environments=[k8s_env])
                break

    print(f"Download SCN isntaller for cluster {cluster_name} [{cluster['id']}]")
    bundle = client.download_installer(cluster['id'])
    with open('__bundle/bundle.tgz', 'wb') as f:
        f.write(bundle.read())


def tls_intercept(clean=False):
    policy = client.list_connections_policy()
    rname = f"Intercept {config['PAYPAL_EXTERNAL_API']}"

    found = False
    for rule in policy['userRules']:
        if rule['name'] == rname:
            found = True
            break

    if found:
        policy['userRules'].remove(rule)

    if not clean:
        newrule = portshift_cli.ConnectionUserRule(
            name=rname,
            source_part_type=portshift_cli.ConnectionUserRuleEndpointPart("PodAnyConnectionRulePart"),
            destination_part_type=portshift_cli.ConnectionUserRuleEndpointPart("FqdnConnectionRulePart",
                                                                               fqdnAddresses=[
                                                                                   config['PAYPAL_EXTERNAL_API']]),
            layer7_settings=portshift_cli.HttpLayer7Part(methods=["GET", "POST"], paths=[], isIntercept=True),
            action="ALLOW",
        )

        policy['userRules'].append(newrule.get_formatted_dict())

    client.send_connections_policy_raw(user_rules=policy['userRules'])


def crud_policy(clean=False):
    policy = client.list_connections_policy()
    rname = f"Block {config['PAYMENT_INTERNAL_API']}"

    found = False
    for rule in policy['userRules']:
        if rule['name'] == rname:
            found = True
            break

    if found:
        policy['userRules'].remove(rule)

    if not clean:
        newrule = portshift_cli.ConnectionUserRule(
            name=rname,
            source_part_type=portshift_cli.ConnectionUserRuleEndpointPart("PodAnyConnectionRulePart"),
            destination_part_type=portshift_cli.ConnectionUserRuleEndpointPart("PodNameConnectionRulePart",
                                                                               names=[config['PAYMENT_INTERNAL_API']]),
            layer7_settings=portshift_cli.HttpLayer7Part(methods=["GET", "POST"], paths=[], isIntercept=False),
            action="BLOCK",
        )
        policy['userRules'].append(newrule.get_formatted_dict())

    client.send_connections_policy_raw(user_rules=policy['userRules'])


def token_injection(clean=False):
    tokens = client.list_tokens()
    found = False
    for token in tokens:
        if token["name"] == config['VAULT_PATH']:
            found = True
            break

    if found:
        client.delete_token(token["id"])

    if not clean:
        apis = client.list_external_catalogs_apis()
        found = False
        for api in apis['items']:
            if api['name'] == config['PAYPAL_EXTERNAL_API']:
                found = True
                break

        if not found: raise Exception("External API not found")

        newtoken = {
            "name": config['VAULT_PATH'],
            "apis": [
                api['identifier']
            ],
            "httpPath": "", # "expirationDate": "2030-07-30T22:00:00.000Z",
            "attributeType": "REQUEST_HEADER",
            "attributeName": "Authorization",
            "vaultSecretPath": f"{config['VAULT_ENGINE']}/data/{config['VAULT_PATH']}#{config['VAULT_KEY']}"
        }

        _token = client.create_token(newtoken)

    policy = client.list_apps_policy()
    found = False
    for rule in policy['userRules']:
        if rule['name'] == config['VAULT_PATH']:
            found = True
            break

    if found: policy['userRules'].remove(rule)

    if not clean:
        newrule = {
            "name": config['VAULT_PATH'],
            "status": "ENABLED",
            "app": {
                "workloadRuleType": "PodNameWorkloadRuleType",
                "names": [
                    config['INJECT_POD']
                ],
                "podValidation": {
                    "vulnerability": None,
                    "podSecurityPolicy": None,
                    "apiSecurityPolicy": None
                }
            },
            "scope": {
                "workloadRuleScopeType": "AnyRuleType"
            },
            "groupName": None,
            "ruleOrigin": "USER",
            "ruleTypeProperties": {
                "ruleType": "InjectionRuleType",
                "tokens": [
                    {
                        "tokenId": _token['id'],
                        "envVariable": config["INJECT_ENVVAR"]
                    }
                ]
            }
        }
        policy['userRules'].append(newrule)

    client.send_app_policy_raw(policy)


def spec_auditing(clean=False):
    if clean:
        # TODO Remove specs. Not strictly needed, skip it for now.
        return

    base_dir = os.path.dirname(__file__)

    # Upload Internal Spec User service
    internal_spec_path = os.path.join(base_dir, config['USER_INTERNAL_API_SPEC'])
    internal_spec_found = False
    internal_spec = open(internal_spec_path, )
    internal_spec_data = json.load(internal_spec)
    internal_apis = client.list_internal_catalogs_apis()
    for api in internal_apis['items']:
        if api['name'] == config['USER_INTERNAL_API']:
            internal_spec_found = True
            client.upload_api_spec(api['identifier'], internal_spec_data)
            break

    if not internal_spec_found: raise Exception("Internal API User not found")

    # Upload Internal Spec Catalogue service
    internal_spec_path = os.path.join(base_dir, config['CATALOGUE_INTERNAL_API_SPEC'])
    internal_spec_found = False
    internal_spec = open(internal_spec_path, )
    internal_spec_data = json.load(internal_spec)
    internal_apis = client.list_internal_catalogs_apis()
    for api in internal_apis['items']:
        if api['name'] == config['CATALOGUE_INTERNAL_API']:
            internal_spec_found = True
            client.upload_api_spec(api['identifier'], internal_spec_data)
            break

    if not internal_spec_found: raise Exception("Internal API Catalogue not found")

    # Upload Internal Spec Order service
    internal_spec_path = os.path.join(base_dir, config['ORDERS_INTERNAL_API_SPEC'])
    internal_spec_found = False
    internal_spec = open(internal_spec_path, )
    internal_spec_data = json.load(internal_spec)
    internal_apis = client.list_internal_catalogs_apis()
    for api in internal_apis['items']:
        if api['name'] == config['ORDERS_INTERNAL_API']:
            internal_spec_found = True
            client.upload_api_spec(api['identifier'], internal_spec_data)
            break

    if not internal_spec_found: raise Exception("Internal API Order not found")

    # Upload Internal Spec Payment service
    internal_spec_path = os.path.join(base_dir, config['PAYMENT_INTERNAL_API_SPEC'])
    internal_spec_found = False
    internal_spec = open(internal_spec_path, )
    internal_spec_data = json.load(internal_spec)
    internal_apis = client.list_internal_catalogs_apis()
    for api in internal_apis['items']:
        if api['name'] == config['PAYMENT_INTERNAL_API']:
            internal_spec_found = True
            client.upload_api_spec(api['identifier'], internal_spec_data)
            break

    if not internal_spec_found: raise Exception("Internal API Payment not found")

    # Upload External Spec Paypal
    external_spec_path = os.path.join(base_dir, config['PAYPAL_EXTERNAL_API_SPEC'])
    external_spec_found = False
    external_spec = open(external_spec_path, )
    external_spec_data = json.load(external_spec)

    external_apis = client.list_external_catalogs_apis()
    for api in external_apis['items']:
        if api['name'] == config['PAYPAL_EXTERNAL_API']:
            external_spec_found = True
            client.upload_api_spec(api['identifier'], external_spec_data)
            break

    if not external_spec_found: raise Exception("External API Paypal not found")

def patch_deployment(clean=False):
    base_dir = os.path.dirname(__file__)
    secure_cn_deployment_path = os.path.join(base_dir,"../001_demo_scn_setup/__bundle/securecn_bundle.yml")
    trace_analyzer_deployment_path = os.path.join(base_dir, "../001_demo_scn_setup/__bundle/trace_analyzer.yml")
    with open(secure_cn_deployment_path, 'r') as stream:
        try:
            docs = yaml.safe_load_all(stream)
            for doc in docs:
                if doc is not None and doc["kind"] == "Deployment" and doc["metadata"]["name"] == "scn-trace-analyzer":
                    if not clean:
                        doc["spec"]["template"]["spec"]["containers"][0]["env"].append(
                            dict(name='NB_OBS_REPORT', value='1'))
                    break
        except Exception as exc:
            print(exc)
    with open(trace_analyzer_deployment_path, 'w') as stream:
        yaml.safe_dump(doc, stream)



def trace_analyzer(clean=False):
    clusters = client.list_kubernetes_clusters()
    for cluster in clusters:
        if cluster['name'] == config['SCN_CLUSTER_NAME']:
            break
    
    
    cluster_id = cluster["id"]
    del cluster["id"]
    
    cluster["tracingSupportSettings"]["traceAnalyzerEnabled"] = (clean == False)
    client.update_kubernetes_clusters(cluster_id, cluster)


def fuzzing(clean=False):
    if clean:
        # TODO: Remove Fuzzer from cluster (not needed yet)
        return

    clusters = client.list_kubernetes_clusters()
    for cluster in clusters:
        if cluster['name'] == config['SCN_CLUSTER_NAME']:
            cluster_id = cluster["id"]
            cluster['apiIntelligenceDAST'] = True
            del cluster["id"]
            client.update_kubernetes_clusters(cluster_id, cluster)
            break

    apis = client.list_internal_catalogs_apis()
    for api in apis['items']:
        if api['name'] == config['PAYMENT_INTERNAL_API']:
            client.fuzz_api(api['identifier'])
            break


def spec_reconstructor(clean=False):
    catalogue_id = None

    if clean:
        # TODO. To be implemented.
        return

    # 1. Get catalogue_id of API to be reconstructed.
    internal_spec_found = False
    internal_apis = client.list_internal_catalogs_apis()
    for api in internal_apis['items']:
        if api['name'] == config['USER_INTERNAL_API']:
            internal_spec_found = True
            catalogue_id = api["identifier"]
            break
    if not internal_spec_found: raise Exception("Internal API User not found")


    # 2. Start learning process
    clusters = client.list_kubernetes_clusters()
    for cluster in clusters:
        if cluster['name'] == config['SCN_CLUSTER_NAME']:
            break

    cluster_id = cluster["id"]
    client.learn_api(catalogue_id, cluster_id, 1)
    print(catalogue_id)
    time.sleep(2)

    # 3. Generate traffic
    try:
        base_dir = os.path.dirname(__file__)
        load_model_path = os.path.join(base_dir, "../tools/load_model.yaml")
        with open(load_model_path, 'r') as mf:
            m = yaml.safe_load(mf)
        sock_shop_client = SockShopClient("http://localhost:8079")
        counter = 10
        for x in range(counter):
            gen = SockShopLoadGen(sock_shop_client, m)
            gen.generate()
    except Exception as e:
        print(e)
        pass
    finally:
        while True:
            status = client.check_learn_status(catalogue_id)
            print("Learning status: {} ...".format(status["response"]["status"]))
            time.sleep(1)
            if status["response"]["status"] == "DONE":
                break

        review_items = client.review_items(catalogue_id)

        # 6. Approve
        del review_items["reviewId"]
        client.approve_review(catalogue_id, review_items)


actions = {
    "setup": setup,
    "patch-deployment": patch_deployment,
    "tls-intercept": tls_intercept,
    "token-injection": token_injection,
    "crud-policy": crud_policy,
    "spec-auditing": spec_auditing,
    "trace-analyzer": trace_analyzer,
    "fuzzing": fuzzing,
    "spec-reconstructor": spec_reconstructor
}


def main(envfile, action, clean):
    load_config(envfile)
    scn_connect()
    print(f"Calling action {action}")
    actions[action](clean=clean)


if __name__ == "__main__":
    try:
        envfile = sys.argv[1]
        action = sys.argv[2]
        clean = (len(sys.argv) > 3 and sys.argv[3] == "clean")

        main(envfile, action, clean)
        print(f'Demo action {action} completed succesfully')
    except Exception as exc:
        traceback.print_exc()
        sys.exit(1)
