import os
import time

import dotenv
import portshift_cli
import yaml
from behave import given, when, then
from sockshop_client import SockShopClient, SockShopLoadGen

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
    config_path = os.path.join(base_dir, '../../../../../config.sh')
    config = dotenv.dotenv_values(config_path)
    client = portshift_cli.scn_connect(config)

    api_endpoints["PAYMENT"] = "http://localhost:8002/paymentAuth"
    request_body["PAYMENT"] = "{}"
    data["given_api_list"] = []
    data["api"] = []


@given(u'a cluster name')
def step_impl(context):
    assert config['SCN_CLUSTER_NAME'] != ""


@when(u'i query the snc dashboard for created clusters')
def step_impl(context):
    clusters = client.list_dashboard_clusters()
    for cluster in clusters:
        if cluster['name'] == config['SCN_CLUSTER_NAME']:
            data["CLUSTER"] = cluster['name']
            break
    assert data["CLUSTER"] == config['SCN_CLUSTER_NAME']


@then(u'response body should not be empty')
def step_impl(context):
    clusters = client.list_dashboard_clusters()
    for cluster in clusters:
        if cluster['name'] == config['SCN_CLUSTER_NAME']:
            data["CLUSTER"] = cluster['name']
            break
    assert data["CLUSTER"] != ""


@then(u'returned cluster list should contain initial cluster name')
def step_impl(context):
    clusters = client.list_dashboard_clusters()
    for cluster in clusters:
        if cluster['name'] == config['SCN_CLUSTER_NAME']:
            data["CLUSTER"] = cluster['name']
            break
    assert data["CLUSTER"] == config['SCN_CLUSTER_NAME']


@given(u'a dashboard (SCN) endpoint url')
def step_impl(context):
    assert config['SCN_HOST'] != ""


@given(u'the sock-shop frontend url')
def step_impl(context):
    assert config['SCN_HOST'] != ""


@given('a list of APIs')
def step_impl(context):
    for row in context.table:
        data["given_api_list"].append(row['api'])
    assert len(data["given_api_list"]) != 0


@when(u'i place an order by navigating to the frontend url, putting a sock in the cart and checking out.')
def step_impl(context):
    try:
        sock_shop_client = SockShopClient("http://localhost:8079")
        sock_shop_client.register(username="mn5", password="mn5", firstName="a", lastName="b", email="a@b.com")
        tags = sock_shop_client.get_tags()

        catalogue = sock_shop_client.get_catalogue(tags=tags)

        sock_shop_client.add_to_cart(catalogue[0]['id'])
        sock_shop_client.login("mn5", "mn5")
        sock_shop_client.add_address(street="Via", postcode="20100", city="Milan", country="Italy", number="0")

        sock_shop_client.add_credit_card(longnum="12344566788", expires="01/22", ccv="123")

        sock_shop_client.checkout()
    except Exception as e:
        print(e)
        pass
    finally:
        pass


@when(u'i query the snc dashboard for created APIs')
def step_impl(context):
    time.sleep(10)
    internal_apis = client.list_internal_catalogs_apis()
    external_apis = client.list_external_catalogs_apis()
    for api in internal_apis['items']:
        data["api"].append(api['name'])
    for api in external_apis['items']:
        data["api"].append(api['name'])
    assert len(data["api"]) != 0


@then(u'the returned API list should match those at hand')
def step_impl(context):
    data["given_api_list"].sort()
    data["api"].sort()
    assert data["given_api_list"] == data["api"]
