import json
import os
import time

import dotenv
from behave import given, when, then

import portshift_cli

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
    context.config.setup_logging()
    global scn_url
    global client
    global base_dir
    global config

    base_dir = os.path.dirname(__file__)
    config_path = os.path.join(base_dir, '../../../../config.sh')
    config = dotenv.dotenv_values(config_path)
    client = portshift_cli.scn_connect(config)

    data["given_api_list"] = []
    data["api"] = []
    data["api_full"] = []
    data["api_risks"] = []
    data["RECONSTRUCTED_INTERNAL_API"] = {}
    data["RECONSTRUCTED_EXTERNAL_API"] = {}


@given(u'2 APIs, "{internal_api}" (internal API) and "{external_api}" (external API).')
def step_impl(context, internal_api, external_api):
    data["given_api_list"].append(internal_api)
    data["given_api_list"].append(external_api)
    assert internal_api != ""
    assert external_api != ""


@when(u'i query the (SNC) API endpoint for "{internal_api}" & "{external_api}" APIs.')
def step_impl(context, internal_api, external_api):
    internal_apis = client.list_internal_catalogs_apis()
    internal_api_found = False
    for api in internal_apis['items']:
        if api["name"] == internal_api:
            internal_api_found = True
            data["api"].append(api["name"])
            break

    external_apis = client.list_external_catalogs_apis()
    time.sleep(10)
    external_api_found = False
    for api in external_apis['items']:
        if api["name"] == external_api:
            external_api_found = True
            data["api"].append(api["name"])
            break
    assert internal_api_found == True
    assert external_api_found == True


@then(u'the returned API list should match those at hand')
def step_impl(context):
    data["given_api_list"].sort()
    data["api"].sort()
    assert data["given_api_list"] == data["api"]


@given(u'the following API specs with risks.')
def step_impl(context):
    internal_spec = open(config["PAYMENT_INTERNAL_API_SPEC"], )
    data["INITIAL_INTERNAL_API_SPEC"] = json.load(internal_spec)

    external_spec = open(config["PAYPAL_EXTERNAL_API_SPEC"], )
    data["INITIAL_EXTERNAL_API_SPEC"] = json.load(external_spec)

    for row in context.table:
        _api = ApiObject(
            row['name'],
            row['category'],
            row['overall'],
            row['critical'],
            row['high'],
            row['medium'],
            row['low'],
            row['unknown'])

        api_risk = _api.__dict__

        data["api_risks"].append(api_risk)
    assert len(data['api_risks']) != 0
    assert data["INITIAL_INTERNAL_API_SPEC"] != ""
    assert data["INITIAL_EXTERNAL_API_SPEC"] != ""


@when(u'i query the (SNC) API endpoint for the given APIs.')
def step_impl(context):
    internal_apis = client.list_internal_catalogs_apis()
    for api in internal_apis['items']:
        if api['name'] == config['PAYMENT_INTERNAL_API']:
            data["RECONSTRUCTED_INTERNAL_API"] = client.fetch_open_api_specs(api['identifier'])
            in_api = client.fetch_internal_api_specs_by_id(api['identifier'])
            data["api_full"].append(in_api)
            break
    external_apis = client.list_external_catalogs_apis()
    for api in external_apis['items']:
        if api['name'] == config['PAYPAL_EXTERNAL_API']:
            data["RECONSTRUCTED_EXTERNAL_API"] = client.fetch_open_api_specs(api['identifier'])
            ex_api = client.fetch_external_api_specs_by_id(api['identifier'])
            data["api_full"].append(ex_api)
            break


@then(u'the returned results should not be empty')
def step_impl(context):
    assert data["RECONSTRUCTED_INTERNAL_API"] != ""
    assert data["RECONSTRUCTED_EXTERNAL_API"] != ""


@then(u'the risks of the returned APIs should match those given')
def step_impl(context):
    for api_risk in data["api_risks"]:
        for api_full in data["api_full"]:
            if api_risk["name"] == api_full["name"]:
                assert api_risk["overall"] == str(api_full["score"]["api"]["categories"]["api-specification"]["risk"])
                assert api_risk["critical"] == str(
                    api_full["score"]["api"]["categories"]["api-specification"]["critical"]["count"])
                assert api_risk["high"] == str(
                    api_full["score"]["api"]["categories"]["api-specification"]["high"]["count"])
                assert api_risk["medium"] == str(
                    api_full["score"]["api"]["categories"]["api-specification"]["medium"]["count"])
                assert api_risk["low"] == str(
                    api_full["score"]["api"]["categories"]["api-specification"]["low"]["count"])
                assert api_risk["unknown"] == str(
                    api_full["score"]["api"]["categories"]["api-specification"]["unclassified"]["count"])


class ApiObject(object):
    def __init__(self, name, category, overall, critical, high, medium, low, unknown):
        self.name = name
        self.category = category
        self.overall = overall
        self.critical = critical
        self.high = high
        self.medium = medium
        self.low = low
        self.unknown = unknown
