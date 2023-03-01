import os
import time

import dotenv
import portshift_cli
import yaml
from behave import given, when, then
from sockshop_client import SockShopClient, SockShopLoadGen

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
    config_path = os.path.join(base_dir, '../../../../../config.sh')
    config = dotenv.dotenv_values(config_path)
    client = portshift_cli.scn_connect(config)

    accounts = client.list_accounts('demo user')
    account_id = accounts[0]["id"]
    data["given_api_list"] = []
    data["api"] = []
    data["orders"] = []
    data["api_full"] = []
    data["risks"] = {}
    data["RECONSTRUCTED_INTERNAL_API"] = {}
    data["RECONSTRUCTED_EXTERNAL_API"] = {}
    client.assign_account(account_id)
    assert config['SCN_HOST'] != ""


@given(u'the sock-shop frontend url')
def step_impl(context):
    assert config['SCN_HOST'] != ""


@given('the following "{application_category}" traces')
def step_impl(context, application_category):
    data["risks"][application_category] = []
    for row in context.table:
        _risk = Risk(
            row['api'],
            row['critical'],
            row['overall'],
            row['critical'],
            row['high'],
            row['medium'],
            row['low'],
            row['unknown']
        )
        _risk = _risk.__dict__
        data["risks"][application_category].append(_risk)
    assert len(data["risks"][application_category]) != 0


@given('the following traces for "{authentication_category}"')
def step_impl(context, authentication_category):
    data["risks"][authentication_category] = []
    for row in context.table:
        _risk = Risk(
            row['api'],
            row['critical'],
            row['overall'],
            row['critical'],
            row['high'],
            row['medium'],
            row['low'],
            row['unknown']
        )
        _risk = _risk.__dict__
        data["risks"][authentication_category].append(_risk)

    assert len(data["risks"][authentication_category]) != 0


@when(u'i place an order by navigating to the frontend url, putting a pair socks in the cart and checking out')
def step_impl(context):
    try:
        sock_shop_client = SockShopClient("http://localhost:8079")
        sock_shop_client.register(username="m5", password="m5", firstName="a", lastName="b", email="a@b.com")
        tags = sock_shop_client.get_tags()

        catalogue = sock_shop_client.get_catalogue(tags=tags)

        sock_shop_client.add_to_cart(catalogue[0]['id'])
        sock_shop_client.login("m5", "m5")
        sock_shop_client.add_address(street="Via", postcode="20100", city="Milan", country="Italy", number="0")

        sock_shop_client.add_credit_card(longnum="12344566788", expires="01/22", ccv="123")

        sock_shop_client.checkout()
    except Exception as e:
        print(e)
        pass
    finally:
        pass


@when(u'i query the portshift (SNC) API endpoint for available traces')
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


@then(u'the returned traces should match those given')
def step_impl(context):
    for api in data["risks"]["application"]:
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

    for api in data["risks"]["authentication"]:
        for api_full in data["api_full"]:
            if api["api"] == api_full["name"] and "authentication" in api_full["score"]["api"]["categories"]:
                assert api["critical"] == str(
                    api_full["score"]["api"]["categories"]["authentication"]["critical"]["count"])
                assert api["high"] == str(
                    api_full["score"]["api"]["categories"]["authentication"]["high"]["count"])
                assert api["medium"] == str(
                    api_full["score"]["api"]["categories"]["authentication"]["medium"]["count"])
                assert api["low"] == str(
                    api_full["score"]["api"]["categories"]["authentication"]["low"]["count"])
                assert api["unknown"] == str(
                    api_full["score"]["api"]["categories"]["authentication"]["unclassified"]["count"])


class Risk(object):
    def __init__(self, api, category, overall, critical, high, medium, low, unknown):
        self.api = api
        self.category = category
        self.overall = overall
        self.critical = critical
        self.high = high
        self.medium = medium
        self.low = low
        self.unknown = unknown
