import json
import os
import random
import string
import time

import dotenv
import portshift_cli
from behave import given, when, then
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

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


def before_all(context):
    context.config.setup_logging()
    global scn_url
    global client
    global base_dir
    global config

    base_dir = os.path.dirname(__file__)
    config_path = os.path.join(base_dir, '../../../../../config.sh')
    config = dotenv.dotenv_values(config_path)
    print(config)
    time.sleep(2)
    client = portshift_cli.wait_for_healthy_cluster(config['SCN_HOST'])
    client.login(config['SCN_USERNAME'], config['SCN_PASSWORD'])
    accounts = client.list_accounts('demo user')
    account_id = accounts[0]["id"]
    api_endpoints["PAYMENT"] = "http://localhost:8002/paymentAuth"
    request_body["PAYMENT"] = "{}"
    client.assign_account(account_id)


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
    time.sleep(2)
    client = portshift_cli.wait_for_healthy_cluster(config['SCN_HOST'])
    client.login(config['SCN_USERNAME'], config['SCN_PASSWORD'])
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
    options = webdriver.ChromeOptions()
    options.headless = False
    browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    browser.implicitly_wait(4)
    browser.get("http://localhost:8079")

    time.sleep(2)
    browser.find_element_by_id("register").click()
    time.sleep(2)
    browser.find_element_by_id("register-username-modal").send_keys(
        ''.join(random.choice(string.ascii_lowercase) for i in range(5)))
    time.sleep(1)
    browser.find_element_by_id("register-first-modal").send_keys("james")
    time.sleep(1)
    browser.find_element_by_id("register-last-modal").send_keys("brown")
    time.sleep(1)
    browser.find_element_by_id("register-email-modal").send_keys("james.brown@email.com")
    time.sleep(1)
    browser.find_element_by_id("register-password-modal").send_keys("james.brown995")

    browser.find_element_by_xpath("//*[@id='register-modal']/div/div/div[2]/form/p/button").click()
    time.sleep(5)

    browser.find_element_by_id("tabCatalogue").click()
    browser.find_element_by_xpath('//*[@id="filters"]/div[4]/label/input').click()
    time.sleep(1)

    browser.find_element_by_xpath('//*[@id="filters-form"]/a').click()
    time.sleep(1)

    browser.find_element_by_xpath('//*[@id="products"]/div[1]/div/div[2]/p[2]/a[2]').click()
    time.sleep(1)

    browser.find_element_by_id("numItemsInCart").click()

    time.sleep(2)

    browser.find_element_by_xpath('//*[@id="add_shipping"]/a').click()
    time.sleep(2)
    browser.find_element_by_name("house-number").send_keys("128")
    time.sleep(1)
    browser.find_element_by_name("street").send_keys("Bayreuth Str.")
    time.sleep(1)
    browser.find_element_by_name("city").send_keys("Duisburg")
    time.sleep(1)
    browser.find_element_by_name("post-code").send_keys("452345")
    time.sleep(1)
    browser.find_element_by_name("country").send_keys("Germany")
    time.sleep(1)
    browser.find_element_by_xpath('//*[@id="form-address"]/p/button').click()
    time.sleep(2)

    browser.find_element_by_xpath('//*[@id="add_payment"]/a').click()
    time.sleep(1)
    browser.find_element_by_name("card-number").send_keys("3445-2233-0998-09982")
    time.sleep(1)
    browser.find_element_by_name("expires").send_keys("07/26")
    time.sleep(1)
    browser.find_element_by_name("ccv").send_keys("455")
    time.sleep(1)
    browser.find_element_by_xpath('//*[@id="card-modal"]/div/div/div[2]/p/button').click()
    time.sleep(2)

    browser.find_element_by_id("orderButton").click()
    time.sleep(2)
    orders = browser.find_element_by_xpath('//*[@id="tableOrders"]//*')
    data["orders"].append(orders)
    time.sleep(2)


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
