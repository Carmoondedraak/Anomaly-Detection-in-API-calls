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
    options = webdriver.ChromeOptions()
    options.headless = False
    browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    #
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
    browser.find_element_by_name("card-number").send_keys("3445-2233-0998-0982")
    time.sleep(1)
    browser.find_element_by_name("expires").send_keys("07/26")
    time.sleep(1)
    browser.find_element_by_name("ccv").send_keys("455")
    time.sleep(1)
    browser.find_element_by_xpath('//*[@id="card-modal"]/div/div/div[2]/p/button').click()
    time.sleep(2)

    browser.find_element_by_id("orderButton").click()
    time.sleep(3)


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
