from typing import Type
from flaskr import db
from flask import json

class Courier(db.Model):
    ID=db.Column('ID', db.String(28), primary_key=True)
    email=db.Column('email', db.String(100), nullable=False)
    name=db.Column('name', db.String(30), default=None)
    maxWidth=db.Column('maxWidth', db.Float, default=None)
    maxLength=db.Column('maxLength', db.Float, default=None)
    maxHeight=db.Column('maxHeight', db.Float, default=None)
    tags=db.Column('tags', db.Text, default=None)

    def __init__(self, ID, email, name=None, maxWidth=None, maxLength=None, maxHeight=None, tags=None):
        self.ID=ID
        self.email=email
        self.name=name
        self.maxWidth=maxWidth
        self.maxLength=maxLength
        self.maxHeight=maxHeight
        self.tags=tags

    def __repr__(self):
        return f"Courier('{self.ID}', '{self.email}', '{self.name}', '{self.maxWidth}', '{self.maxLength}', '{self.maxHeight}', '{self.tags}')"
    
    def json(self):
        data = {
            "ID": self.ID,
            "email": self.email,
            "name": self.name,
            "maxDimension": {
                "maxWidth": self.maxWidth,
                "maxLength": self.maxLength,
                "maxHeight": self.maxHeight
                },
            "tags": self.tags
        }
        return json.dumps(data)
        
class Trip(db.Model):
    ID=db.Column('ID', db.String(28), primary_key=True)
    courierID=db.Column('courierID', db.String(28), nullable=None)
    orderID=db.Column('orderID', db.String(28), nullable=None)
    distance=db.Column('distance', db.Float, nullable=None)
    assignedAt=db.Column('assignedAt', db.String(30), nullable=None)
    pickedAt=db.Column('pickedAt', db.String(30), nullable=None)
    deliveredAt=db.Column('deliveredAt', db.String(30), nullable=None)

    def __init__(self, ID, courierID, orderID, distance, assignedAt, pickedAt, deliveredAt):
        self.ID=ID
        self.courierID=courierID
        self.orderID=orderID
        self.distance=distance
        self.assignedAt=assignedAt
        self.pickedAt=pickedAt
        self.deliveredAt=deliveredAt

    def __repr__(self):
        return f"Trip('{self.ID}', '{self.courierID}', '{self.orderID}', '{self.distance}', '{self.assignedAt}', '{self.pickedAt}', '{self.deliveredAt}',)"
            
    def json(self):
        data = {
            "ID": self.ID,
            "courierID": self.courierID,
            "orderID": self.orderID,
            "distance": self.distance,
            "assignedAt": self.assignedAt,
            "pickedAt": self.pickedAt,
            "deliveredAt": self.deliveredAt
        }
        return json.dumps(data)