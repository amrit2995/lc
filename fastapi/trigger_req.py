import requests

url = "http://localhost:8000/user_agent"

response = requests.post(
    url,
    headers={
        "User-Agent": "test"
    }
)
print(response.text)


url = "http://localhost:8000/body"

response = requests.post(
    url,
    json={
        "name": "test"
    }
)
print(response.text)