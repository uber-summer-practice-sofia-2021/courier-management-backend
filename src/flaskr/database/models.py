import uuid
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Courier(db.Model):
    id = db.Column("id", db.String(36), primary_key=True)
    email = db.Column("email", db.String(100), nullable=False, unique=True)
    name = db.Column("name", db.String(30),nullable=False,default='')
    max_weight = db.Column("max_weight", db.Float,nullable=False, default=0)
    max_width = db.Column("max_width", db.Float,nullable=False, default=0)
    max_length = db.Column("max_length", db.Float,nullable=False, default=0)
    max_height = db.Column("max_height", db.Float,nullable=False, default=0)
    tags = db.Column("tags", db.Text, nullable=False,default='')
    is_validated = db.Column("is_validated", db.Boolean, default=False)

    def __init__(self, email):
        self.id = str(uuid.uuid4())
        self.email = email

    def __repr__(self):
        return f"Courier('{self.id}', '{self.email}', '{self.name}', '{self.max_weight}', '{self.max_width}', '{self.max_length}', '{self.max_height}', '{self.tags}','{self.is_validated}')"

    """ Returns a dictionary of the object """

    def map(self):
        data = {
            "ID": self.id,
            "email": self.email,
            "name": self.name,
            "maxWeight": self.max_weight,
            "maxWidth": self.max_width,
            "maxLength": self.max_length,
            "maxHeight": self.max_height,
            "tags": [x for x in self.tags.split(",") if x],
        }
        return data


class Trip(db.Model):
    id = db.Column("id", db.String(36), primary_key=True)
    courier_id = db.Column(
        "courier_id", db.String(36), db.ForeignKey("courier.id"), nullable=False
    )
    order_id = db.Column("order_id", db.String(36), nullable=False, unique=True)
    distance = db.Column("distance", db.Float, default=0)
    assigned_at = db.Column("assigned_at", db.String(30))
    picked_at = db.Column("picked_at", db.String(30))
    delivered_at = db.Column("delivered_at", db.String(30))

    courier = db.relationship("Courier", backref=db.backref("trips", lazy=True))

    def __init__(self, courier_id, order_id):
        self.id = str(uuid.uuid4())
        self.courier_id = courier_id
        self.order_id = order_id

    def __repr__(self):
        return f"Trip('{self.id}', '{self.courier_id}', '{self.order_id}', '{self.distance}', '{self.assigned_at}', '{self.picked_at}', '{self.delivered_at}',)"

    """ Returns a dictionary of the object """

    def map(self):
        data = {
            "ID": self.id,
            "courierID": self.courier_id,
            "orderID": self.order_id,
            "distance": self.distance,
            "assignedAt": self.assigned_at,
            "pickedAt": self.picked_at,
            "deliveredAt": self.delivered_at,
        }
        return data

    def array(self):
        return [self.id,self.courier_id,self.order_id,self.distance,self.assigned_at,self.picked_at,self.delivered_at,]

