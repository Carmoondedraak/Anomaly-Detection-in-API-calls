# kubectl -n sock-shop port-forward deployment/front-end 8079:8079
import random
import requests
import sys
from requests.auth import HTTPBasicAuth
import json
import yaml


class SockShopClient(object):
    def __init__(self, url):
        self._url = url
        self._session = None

    def _build_url(self, url):
        return self._url + url

    def login(self, username, password):
        self._s = requests.Session()
        self._s.headers.update({'content-type': 'application/json'})
        self._s.get(self._build_url('/login'), auth=HTTPBasicAuth(username, password))
        print(self._s.cookies)

    def logout(self):
        self._s = None

    def register(self, username, password, email, firstName, lastName):
        self._s = requests.Session()
        self._s.headers.update({'content-type': 'application/json'})

        data = {
            'username': username,
            'password': password,
            'email': email,
            'firstName': firstName,
            'lastName': lastName
        }
        return self._s.post(self._build_url('/register'), data=json.dumps(data))

    def get_tags(self):
        res = requests.get(self._build_url('/tags'))
        if res.status_code != 200 or res.json()['err']:
            raise Exception(f"Failed to get tags: {res} {res.json().get('err')}")
        return res.json()['tags']

    def get_catalogue(self, tags=[]):
        params = {
            'tags': ','.join(tags),
            'page': 1,
            'size': 100
        }
        res = requests.get(self._build_url('/catalogue'), params=params)
        if res.status_code != 200:
            raise Exception(f"Failed to get catalogue: {res} {res.json()}")

        return res.json()

    def get_cart(self):
        res = self._s.get(self._build_url('/cart'))
        if res.status_code != 200:
            raise Exception(f"failed to get cart: {res} {res.json()}")

        return res.json()

    def empty_cart(self, cart=None):
        if not cart:
            cart = self.get_cart()
        for item in cart:
            self.remove_from_cart(item['itemId'])

    def add_to_cart(self, item):
        data = {
            'id': item
        }

        res = self._s.post(self._build_url('/cart'), data=json.dumps(data))
        if res.status_code != 201:
            raise Exception(f"Failed to add {item} to cart: {res} {res.json()}")
        return res

    def remove_from_cart(self, item):
        res = self._s.delete(self._build_url(f'/cart/{item}'))
        if res.status_code != 202:
            raise Exception(f"Failed to remove {item} from cart: {res} {res.json()}")

        return res

    def checkout(self):
        res = self._s.post(self._build_url('/orders'))
        return
        if res.status_code != 201:
            raise Exception(f"Failed to checkout: {res} {res.json()}")

    def add_address(self, street, number, city, postcode, country):
        data = {
            "street": street,
            "number": number,
            "city": city,
            "postcode": postcode,
            "country": country
        }
        res = self._s.post(self._build_url('/addresses'), data=json.dumps(data))
        if res.status_code != 200:
            raise Exception(f"Failed to add address: {res} {res.json()}")
        return res.json()

    def get_address(self):
        res = self._s.get(self._build_url('/address'))
        if res.status_code != 200:
            raise Exception(f"Failed to get address: {res} {res.json()}")
        if res.json().get('status_code') == 500:
            return {}
        return res.json()

    def get_card(self):
        res = self._s.get(self._build_url('/card'))
        if res.status_code != 200:
            raise Exception(f"Failed to get card: {res} {res.json()}")
        if res.json().get('status_code') == 500:
            return {}
        return res.json()

    def get_orders(self):
        res = self._s.get(self._build_url('/orders'))
        if res.status_code != 201:
            raise Exception(f"Failed to get orders: {res} {res.json()}")
        return res.json()

    def add_credit_card(self, longnum, expires, ccv):
        data = {
            "longNum": longnum,
            "expires": expires,
            "ccv": ccv,
        }
        res = self._s.post(self._build_url('/cards'), data=json.dumps(data))
        if res.status_code != 200:
            raise Exception(f"Failed to add credit card: {res} {res.json()}")
        return res.json()

    def browse_to_item(self, id):
        res = self._s.get(self._build_url(f'/detail.html?id={id}'))
        if res.status_code not in [304, 200]:
            raise Exception(f"failed to browse to item {id}: {res} ")


class SockShopLoadGen(object):
    def __init__(self, client, model):
        self.model = model
        self.client = client
        self.state = ''
        self.users = []
        self.reset()

    def generate(self):
        # self.state = 'login'
        self.process_state(next='register')
        while self.state != 'end':
            self.process_state()

    def reset(self):
        self.user = {}
        self.cart = {}
        self.item = {}
        self.catalogue = {}

    def process_state(self, next=None):

        s = self.state
        if not next:
            nexts = list(self.model[s].keys())
            weights = [self.model[s][next] for next in nexts]
            next = random.choices(nexts, weights=weights, k=1)[0]
        self.state = next
        client = self.client
        print(f"{s} -> {next}")

        if next == "logout":
            client.logout()
            self.reset()
        elif next == "register":
            self.user = {
                "username": f"user_{len(self.users)}",
                "password": "password",
                "email": "email@email.com",
                "firstName": "John",
                "lastName": "Doe"
            }
            self.users.append(self.user)
            client.register(username=self.user['username'], password=self.user['password'], email=self.user['email'],
                            firstName=self.user['firstName'], lastName=self.user['lastName'])
            client.add_address(street="Via", postcode="20100", city="Milan", country="Italy", number="0")
            client.add_credit_card(longnum="12344566788", expires="01/22", ccv="123")
        elif next == "login":
            if not self.user:
                self.user = random.choice(self.users)
            client.login(self.user['username'], self.user['password'])
        elif next == "get-catalogue":
            tags = client.get_tags()
            _tags = random.choices(tags, k=random.randint(0, len(tags)))
            self.catalogue = client.get_catalogue(_tags)
        elif next == "get-item":
            if len(self.catalogue) == 0:
                self.state = 'get-catalogue'
                return
            self.item = random.choice(self.catalogue)
            client.browse_to_item(self.item['id'])
        elif next == "get-cart":
            self.cart = client.get_cart()
        elif next == "add-to-cart":
            client.add_to_cart(self.item['id'])
        elif next == "remove-from-cart":
            if not self.cart:
                self.state = 'get-cart'
                return
            it = random.choice(self.cart)
            client.remove_from_cart(it['itemId'])
        elif next == "empty-cart":
            client.empty_cart(self.cart)
        elif next == "checkout":
            client.checkout()
        elif next == "end":
            pass
        else:
            raise Exception(f"Unable to process state {next}")


if __name__ == "__main__":
    with open('load_model.yaml', 'r') as mf:
        m = yaml.safe_load(mf)
    if len(sys.argv) > 1:
        # http://34.116.171.22:8079
        sockshopurl = sys.argv[1]
    else:
        sockshopurl = "http://localhost:8079"
    client = SockShopClient(sockshopurl)
    while True:
        gen = SockShopLoadGen(client, m)
        gen.generate()
#     # generate_load(client=client, model=m)
#
#     exit(0)
#     client.login("m5", "m5")
# #    client.register(username="m5", password="m5", firstName="a", lastName="b", email="a@b.com")
#     tags = client.get_tags()
#     catalogue = client.get_catalogue(tags=tags)
#     client.empty_cart()
#     client.add_to_cart(catalogue[0]['id'])
#     cart = client.get_cart()
#     print(cart)
#     print(client.get_address())
#     print(client.get_card())
#     if not client.get_address():
#         client.add_address(street="Via", postcode="20100", city="Milan", country="Italy", number="0")
#     if not client.get_card():
#         client.add_credit_card(longnum="12344566788", expires="01/22", ccv="123")
#     client.checkout()
#     orders = client.get_orders()
#     cart = client.get_cart()
#     print(cart)
#     print(orders)
