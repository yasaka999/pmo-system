from unicodedata import name

from flask import Flask

app = Flask(__name__)


# @app.route("/")
@app.route("/hit/<name>")
def index(name):
    return "<h1>Hello Flask! %s</h1>" % name


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
