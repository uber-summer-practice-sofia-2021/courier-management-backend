from flaskr import api
from flaskr.resources import *

api.add_resource(CourierResource, '/couriers/<string:ID>')
api.add_resource(TripResource, '/trips/<string:ID>')