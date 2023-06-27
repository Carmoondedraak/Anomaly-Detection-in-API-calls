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


@given(u'a Portshift (SNC) API endpoint.')
def step_impl(context):
    global scn_url
    global client
    global base_dir
    global config

    base_dir = os.path.dirname(__file__)
    config_path = os.path.join(base_dir, '../../../../config.sh')
    config = dotenv.dotenv_values(config_path)
    client = portshift_cli.scn_connect(config)

    data["connection_rules"] = []
    data["api"] = []
    data["catalogue_id"] = None
    data["reconstructed_spec"] = {}


@given(u'a "{user}" API.')
def step_impl(context, user):
    internal_apis = client.list_internal_catalogs_apis()
    internal_api_found = False
    for api in internal_apis['items']:
        if api["name"] == user:
            internal_api_found = True
            data["api"].append(api["name"])
            data["catalogue_id"] = api["identifier"]
            break
    assert internal_api_found == True


@when(u'spec reconstruction is performed on the user API.')
def step_impl(context):
    data["reconstructed_spec"] = client.fetch_reconstructed_spec(data["catalogue_id"])


@then(u'the status of the reconstruction process should be "DONE".')
def step_impl(context):
    status = client.check_learn_status(data["catalogue_id"])
    assert status["response"]["status"] == "DONE"


@then(u'the reconstructed spec (file) should not be empty.')
def step_impl(context):
    assert data["reconstructed_spec"] != ""
