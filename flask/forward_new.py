import json, requests, yaml

from flask import Flask, request

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
# read config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

print(config)
@app.route("/requestService", methods=["POST"])
def requestService():
    print(request.headers)
    json_data = request.json
    del_data = config["del_field"]
    modify_data = config["mod_field"]
    print("received data:", json_data)
    [json_data.pop(key, 0) for key in del_data]
    json_data.update(modify_data)
    print("send data:", json_data)
    #headers = {h[0]: h[1] for h in request.headers}
    url = config["forward_url"]
    if "AccountType" not in json_data.keys():
        url = url + "/newurl"  
    print(url)    
    r = requests.request(request.method,
                         url,
                         data=json.dumps(json_data),
                         headers=request.headers)
    print("response data:", r.text)
    return r.content


if __name__ == "__main__":
    app.run(port=config["port"], debug=True)
