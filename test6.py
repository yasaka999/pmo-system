import requests

url = "http://172.16.20.128:8100/v2/vcr/media"

querystring = {"taskId":"pbyk32sxjybak4swz1p"}

headers = {'user-agent': 'vscode-restclient'}

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)