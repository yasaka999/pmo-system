import requests

client = requests.session()
headers = {"Content-Type": "application/json", "Connection": "keep-alive"}
while True:
    url = "http://www.baidu.com"
    r = client.get(url, headers=headers)
    print(r.status_code)
