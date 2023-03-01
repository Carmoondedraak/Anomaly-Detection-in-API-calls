import requests
import json
class MakeApiCall:
    def get_data(self, api):
        response = requests.get(f"{api}")
        if response.status_code == 200:
            print("sucessfully fetched the data")
            print(response)
            self.formatted_print(self, response.json())
        else:
            print(f"Hello person, there's a {response.status_code} error with your request")


    def formatted_print(self, obj):
        text = json.dumps(obj, sort_keys=True, indent=4)
        print(text)

m = MakeApiCall        
m.get_data(m,'http://172.18.0.4:30001/cart')