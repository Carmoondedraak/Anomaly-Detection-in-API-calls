import json
import os
import random
import string
import time

import dotenv
import portshift_cli
import requests
from behave import given, when, then
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

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
    config_path = os.path.join(base_dir, '../../../../config.sh')
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
    payment_path = os.path.join(base_dir, '../../payloads/payment.json')
    with open(payment_path) as f:
        payment_json = json.load(f)

    response = requests.post(url=api_endpoints["PAYMENT_URL"], json=payment_json, headers=request_headers)
    response_body["POST"] = response.json()
    assert response_body["POST"] != ""


@then(u'the payment services should respond with payment status')
def step_impl(context):
    print(response_body["POST"]["authorised"])
    time.sleep(2)
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
    except NoSuchElementException:
        pass


@when(u'the payment should not respond and no orders should be created')
def step_impl(context):
    assert len(data["orders"]) == 0
