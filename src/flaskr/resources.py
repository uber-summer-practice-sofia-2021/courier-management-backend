from flask_restful import Resource
from flaskr.models import *

class CourierResource(Resource):
    def get(self, ID):
        return Courier.query.all()

class TripResource(Resource):
    def get(self, ID):
        return Trip.query.all()