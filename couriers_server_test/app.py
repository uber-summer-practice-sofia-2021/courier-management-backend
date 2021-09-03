from flask import Flask, request, json, Response
import requests

server = Flask(__name__)


@server.route("/hello")
def hello():
    return "Hello World! This is Hristo. Welcome to this page!"

@server.route("/")
def get_data():
    return requests.get("http://127.0.0.1:5000/fixtures").content


