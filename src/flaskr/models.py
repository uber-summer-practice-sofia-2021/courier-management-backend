from flaskr import db

class Courier(db.Model):
    ID=db.Column('ID', db.String(28), primary_key=True)
    email=db.Column('email', db.String(100), nullable=False)
    name=db.Column('name', db.String(30), default=None)
    maxDimension=db.Column('maxDimension', db.String(20), default=None)
    tags=db.Column('tags', db.Text(), default=None)

    def __init__(self, ID, email, name=None, maxDimension=None, tags=None):
        self.ID=ID
        self.email=email
        self.name=name
        self.maxDimension=maxDimension
        self.tags=tags

    def __repr__(self):
        return f"Courier('{self.ID}', '{self.email}', '{self.name}', '{self.maxDimension}', '{self.tags}')"
        
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