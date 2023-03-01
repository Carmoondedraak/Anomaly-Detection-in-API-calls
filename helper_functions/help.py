from locust import HttpUser, TaskSet
from requests_toolbelt.adapters.source import SourceAddressAdapter
import random

def login(l):
    l.client.post("/login", {"username":"ellen_key", "password":"education"})

def logout(l):
    l.client.post("/logout", {"username":"ellen_key", "password":"education"})

def index(l):
    l.client.get("/")

def profile(l):
    l.client.get("/profile")

class UserBehavior(TaskSet):
    tasks = {index: 2, profile: 1}

    def on_start(self):
        # List of IP's that can be used as "source" - hardcoded for simplicity
        ips = ['192.168.100.10', '192.168.100.11', '192.168.100.12', '192.168.100.13']
        i = random.randint(0, len(self.ips)-1)
        self.client.mount("https://", SourceAddressAdapter(self.ips[i]))
        self.client.mount("http://", SourceAddressAdapter(self.ips[i]))
        login(self)

    def on_stop(self):
        logout(self)

class WebsiteUser(HttpUser):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000