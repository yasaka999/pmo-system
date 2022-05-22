from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

@app.route("/aaa", methods=["GET", "POST"])
def aaa():
    print(request.headers)
    json_data = request.json
    print(json_data)
    return jsonify(json_data)

if __name__ == "__main__":
    app.run(port=6000, debug=True)
