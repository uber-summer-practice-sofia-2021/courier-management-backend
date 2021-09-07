import requests

BASE = "http://localhost:5000/couriers"

post_data = {
    "courierID": "7f4dc6b6-f8ba-477b-8b21-25446c9c72b3"
}

response = requests.get(BASE, json=post_data)
print(response.status_code)
print(response.text)