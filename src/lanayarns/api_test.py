import requests
import json

base_url = 'http://localhost:8000/api/'

login_url = base_url + 'auth/token/'
products_url = base_url + 'products/'

# requests.post(login_url, data=None, headers=None, params=None)

# Auth test
data = {
    'username': 'testuser',
    'password': 'test1234',
}

login_r = requests.post(login_url, data=data)

json_data = login_r.json() #login_r.text
print(json.dumps(json_data, indent=2))

token = json_data['token']

# Retrieve products test
headers = {
    'Authorization': 'JWT %s' % (token)
}
p_r = requests.get(products_url, headers=headers)
prod_json_data = p_r.json()
print (json.dumps(prod_json_data, indent=2))
