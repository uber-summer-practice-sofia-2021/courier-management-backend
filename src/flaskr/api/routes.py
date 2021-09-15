from threading import current_thread
from flask import Blueprint, make_response, request, jsonify, json, Response, current_app
from flaskr.database.models import *

api = Blueprint("api", __name__)


# Endpoint for requesting courier info
@api.route("/couriers", methods=["GET"])
def couriers_api():
    try:
        courier_id = request.args["courierID"]
        courier = Courier.query.filter_by(id=courier_id).first().map()
        return Response(response=json.dumps(courier), content_type="application/json")
    except:
        return Response(response=json.dumps(None), status=204, content_type="application/json")


# Endpoint for requesting trip info
@api.route("/trips", methods=["GET"])
def trips_api():
    try:
        trip_id = request.args["tripID"]
        trip = Trip.query.filter_by(id=trip_id).first().map()
        return Response(response=json.dumps(trip), content_type="application/json")
    except:
        return Response(response=json.dumps(None), status=204, content_type="application/json")

# Endpoint for testing orders requests
@api.route("/orders", methods=["GET"])
def orders_api():
    try:
        fixtures_path = "../fixtures/orders.json"
        #fixtures_path = "fixtures/orders.json"
        file = open(fixtures_path)
        data = json.load(file)
        file.close()
        return Response(response=json.dumps(data), content_type="application/json")
    except:
        return Response(response=json.dumps(None), status=204, content_type="application/json")


# Endpoint for testing orders requests
@api.route("/orders/<orderID>", methods=["GET"])
def orders_id_api(orderID):
    try:
        fixtures_path = "../fixtures/orders.json"
        #fixtures_path = "fixtures/orders.json"
        file = open(fixtures_path)
        data = next(x for x in json.load(file)['data'] if x['ID']==orderID)
        return Response(response=json.dumps(data), content_type="application/json")
    except:
        return Response(response=json.dumps(None), status=204, content_type="application/json")