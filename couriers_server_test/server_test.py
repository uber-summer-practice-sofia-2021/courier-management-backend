from flask import Flask, request, json, Response
import os

server = Flask(__name__)


@server.route("/")
def hello():
    return "Hello World!"


@server.route("/hello")
def personalised_hello():
    username = request.args.get('user')
    return f'Hello {username}!'


@server.route("/fixtures", methods=["GET"])
def orders():

    fixtures_path = "../fixtures/courier.json"
    file = open(fixtures_path)
    json_data = json.load(file)
    file.close()
    return Response(json.dumps(json_data), mimetype='application/json')


if __name__ == "__main__":
    server.run(host='0.0.0.0')
