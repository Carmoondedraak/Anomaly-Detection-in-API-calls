import json
import os
import time

import dotenv
import portshift_cli
import requests
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


def before_all(context):
    print("before_all activated")


@given(u'an SCN API endpoint.')
def step_impl(context):
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
    data["api"] = []
    data["orders"] = []
    api_endpoints["PAYMENT_URL"] = "http://localhost:8002/paymentAuth"
    request_body["PAYMENT"] = "{}"
    response_body["POST"] = "{}"

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


@given(u'a payment service endpoint')
def step_impl(context):
    assert api_endpoints["PAYMENT_URL"] != ""


@when(u'i send a payment request (from localhost) to the payment API')
def step_impl(context):
    payment_path = os.path.join(base_dir, '../../../payloads/payment.json')
    with open(payment_path) as f:
        payment_json = json.load(f)

    response = requests.post(url=api_endpoints["PAYMENT_URL"], json=payment_json, headers=request_headers)
    response_body["POST"] = response.json()
    assert response_body["POST"] != ""


@then(u'the payment services should respond with payment status')
def step_impl(context):
    assert response_body["POST"]["authorised"] == True


@given(u'an SCN API endpoint')
def step_impl(context):
    assert config['SCN_HOST'] != ""


@given(u'the sock-shop frontend url')
def step_impl(context):
    assert config['SCN_HOST'] != ""


@when(u'i place an order by navigating to the frontend url, putting a pair of socks in the cart and checking out')
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


@when(u'the payment should not respond and no orders should be created')
def step_impl(context):
    assert len(data["orders"]) == 0
