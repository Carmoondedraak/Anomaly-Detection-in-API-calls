import os
import time

import dotenv
import portshift_cli
from behave import given, when, then

api_endpoints = {}
request_header = {}
request_body = {}
response_code = {}
response_body = {}
data = {}
scn_url = None
client = None
base_dir = None
config = {}


@given(u'an SNC API endpoint')
def step_impl(context):
    context.config.setup_logging()
    global scn_url
    global client
    global base_dir
    global config

    base_dir = os.path.dirname(__file__)
    config_path = os.path.join(base_dir, '../../../../config.sh')
    config = dotenv.dotenv_values(config_path)
    client = portshift_cli.scn_connect(config)
    accounts = client.list_accounts('demo user')
    account_id = accounts[0]["id"]
    data["given_api_list"] = []
    data["api"] = []
    data["orders"] = []
    data["api_full"] = []
    data["findings"] = {}
    data["RECONSTRUCTED_INTERNAL_API"] = {}
    client.assign_account(account_id)
    assert config['SCN_HOST'] != ""


@given(u'the sock-shop frontend url')
def step_impl(context):
    assert config['SCN_HOST'] != ""


@given('the following "{application_category}" findings')
def step_impl(context, application_category):
    data["findings"][application_category] = []
    for row in context.table:
        _finding = Finding(
            row['api'],
            row['critical'],
            row['overall'],
            row['critical'],
            row['high'],
            row['medium'],
            row['low'],
            row['unknown']
        )
        _finding = _finding.__dict__
        data["findings"][application_category].append(_finding)
    assert len(data["findings"][application_category]) != 0


@when(u'i query the portshift (SNC) API endpoint for available findings')
def step_impl(context):
    internal_apis = client.list_internal_catalogs_apis()
    for api in internal_apis['items']:
        if api['name'] == config['PAYMENT_INTERNAL_API']:
            data["RECONSTRUCTED_INTERNAL_API"] = client.fetch_open_api_specs(api['identifier'])
            in_api = client.fetch_internal_api_specs_by_id(api['identifier'])
            data["api_full"].append(in_api)
            break


@then(u'the returned findings should match those given')
def step_impl(context):
    for api in data["findings"]["application"]:
        for api_full in data["api_full"]:
            if api["api"] == api_full["name"] and "application" in api_full["score"]["api"]["categories"]:
                assert api["critical"] == str(
                    api_full["score"]["api"]["categories"]["application"]["critical"]["count"])
                assert api["high"] == str(
                    api_full["score"]["api"]["categories"]["application"]["high"]["count"])
                assert api["medium"] == str(
                    api_full["score"]["api"]["categories"]["application"]["medium"]["count"])
                assert api["low"] == str(
                    api_full["score"]["api"]["categories"]["application"]["low"]["count"])
                assert api["unknown"] == str(
                    api_full["score"]["api"]["categories"]["application"]["unclassified"]["count"])


class Finding(object):
    def __init__(self, api, category, overall, critical, high, medium, low, unknown):
        self.api = api
        self.category = category
        self.overall = overall
        self.critical = critical
        self.high = high
        self.medium = medium
        self.low = low
        self.unknown = unknown
