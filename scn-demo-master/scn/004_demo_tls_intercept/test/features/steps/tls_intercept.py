import os

import dotenv
import portshift_cli
from behave import given, when, then

api_endpoints = {}
request_headers = {}
request_body = {}
response_codes = {}
response_body = {}
data = {}
scn_url = None
client = None
base_dir = None
config = {}


@given(u'a portshift (SNC) API endpoint.')
def step_impl(context):
    global scn_url
    global client
    global base_dir
    global config

    base_dir = os.path.dirname(__file__)
    config_path = os.path.join(base_dir, '../../../../config.sh')
    config = dotenv.dotenv_values(config_path)
    client = portshift_cli.wait_for_healthy_cluster(config['SCN_HOST'])
    client.login(config['SCN_USERNAME'], config['SCN_PASSWORD'])
    accounts = client.list_accounts('demo user')
    account_id = accounts[0]["id"]
    data["connection_rules"] = []
    data["api"] = []
    client.assign_account(account_id)


@given(u'a connection rule "{connection_rule_name}"')
def step_impl(context, connection_rule_name):
    assert connection_rule_name != ""


@when(u'i query the snc dashboard for created connection rules')
def step_impl(context):
    data["connection_rules"] = client.list_connection_rules()
    assert len(data["connection_rules"]) != 0


@then(u'returned connection rules lists should contain "{connection_rule_name}"')
def step_impl(context, connection_rule_name):
    connection_rule_found = False
    for rule in data["connection_rules"]["userRules"]:
        if rule['name'] == connection_rule_name:
            connection_rule_found = True
            break
    assert connection_rule_found
