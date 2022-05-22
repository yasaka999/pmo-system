import json

import requests

from flask import Flask, request

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False


@app.before_request
def proxy():
    print(request.headers)
    json_data = request.json
    del_data = ["TeamID", "City"]
    modify_data = {
        "新字段": "随便定义",
        "Carrier": 5,
        "address": "陕西省西安市雁塔区",
        "name": "张三"
    }
    print("received data:", json_data)
    [json_data.pop(key, 0) for key in del_data]
    json_data.update(modify_data)
    print("send data:", json_data)
    #headers = {h[0]: h[1] for h in request.headers}
    url = "http://192.168.5.183:6000/aaa"
    r = requests.request(request.method,
                         url,
                         data=json.dumps(json_data),
                         headers=request.headers)
    print("response data:", r.text)
    return r.content


if __name__ == "__main__":
    app.run(port=5000, debug=True)
