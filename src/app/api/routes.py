from flask import Blueprint, request, json, Response, current_app
from app.db.models import *
import inspect as ins

api = Blueprint("api", __name__)


# Endpoint for requesting courier info
@api.route("/couriers", methods=["GET"])
def couriers_api():
    courier_id = request.args["courierID"]
    courier = Courier.query.filter_by(id=courier_id).first_or_404().map()
    return Response(response=json.dumps(courier), content_type="application/json", status=302)
    # try:
    #     courier_id = request.args["courierID"]
    #     courier = Courier.query.filter_by(id=courier_id).first().map()
    #     return Response(response=json.dumps(courier), content_type="application/json", status=302)
    # except Exception as e:
    #     current_app.logger.error(
    #         f"{e} -> {ins.getframeinfo(ins.currentframe()).function}"
    #     )
    #     return Response(
    #         response=json.dumps(None), status=204, content_type="application/json"
    #     )


# Endpoint for requesting trip info
@api.route("/trips", methods=["GET"])
def trips_api():
    trip_id = request.args["tripID"]
    trip = Trip.query.filter_by(id=trip_id).first_or_404().map()
    return Response(response=json.dumps(trip), content_type="application/json", status=302)
    # try:
    #     trip_id = request.args["tripID"]
    #     trip = Trip.query.filter_by(id=trip_id).first().map()
    #     return Response(response=json.dumps(trip), content_type="application/json", status=302)
    # except Exception as e:
    #     current_app.logger.error(
    #         f"{e} -> {ins.getframeinfo(ins.currentframe()).function}"
    #     )
    #     return Response(
    #         response=json.dumps(None), status=204, content_type="application/json"
    #     )


# Endpoint for testing orders requests
@api.route("/orders", methods=["GET"])
def orders_api():
    try:
        # fixtures_path = "../fixtures/orders.json"
        fixtures_path = "fixtures/orders.json"
        file = open(fixtures_path)
        data = json.load(file)
        file.close()
        return Response(response=json.dumps(data), content_type="application/json")
    except Exception as e:
        current_app.logger.error(
            f"{e} -> {ins.getframeinfo(ins.currentframe()).function}"
        )
        return Response(
            response=json.dumps(None), status=204, content_type="application/json"
        )


# Endpoint for testing orders requests
@api.route("/orders/<orderID>", methods=["GET"])
def orders_id_api(orderID):
    try:
        # fixtures_path = "../fixtures/orders.json"
        fixtures_path = "fixtures/orders.json"
        file = open(fixtures_path)
        data = next(x for x in json.load(file)["data"] if x["id"] == orderID)
        return Response(response=json.dumps(data), content_type="application/json")
    except Exception as e:
        current_app.logger.error(
            f"{e} -> {ins.getframeinfo(ins.currentframe()).function}"
        )
        return Response(
            response=json.dumps(None), status=204, content_type="application/json"
        )
