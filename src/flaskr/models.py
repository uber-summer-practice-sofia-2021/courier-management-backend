from flaskr import db

class Courier(db.Model):
    id=db.Column('id', db.String(36), primary_key=True)
    email=db.Column('email', db.String(100), nullable=False)
    name=db.Column('name', db.String(30), default=None)
    max_width=db.Column('max_width', db.Float, default=None)
    max_length=db.Column('max_length', db.Float, default=None)
    max_height=db.Column('max_height', db.Float, default=None)
    tags=db.Column('tags', db.Text, default=None)

    def __init__(self, id, email, name=None, max_width=None, max_length=None, max_height=None, tags=None):
        self.id=id
        self.email=email
        self.name=name
        self.max_width=max_width
        self.max_length=max_length
        self.max_height=max_height
        try:
            self.tags=','.join(tags)
        except:
            self.tags=None

    def __repr__(self):
        return f"Courier('{self.id}', '{self.email}', '{self.name}', '{self.max_width}', '{self.max_length}', '{self.max_height}', '{self.tags}')"
    
    """ Returns a dictionary of the object """
    def map(self):
        data = {
            "ID": self.id,
            "email": self.email,
            "name": self.name,
            "maxDimension": {
                "maxWidth": self.max_width,
                "maxLength": self.max_length,
                "maxHeight": self.max_height
                },
            "tags": None
        }
        try:
            data["tags"]=self.tags.split(',')
        except:
            pass
        return data
        
class Trip(db.Model):
    id=db.Column('id', db.String(36), primary_key=True)
    courier_id=db.Column('courier_id', db.String(36), db.ForeignKey('courier.id'), nullable=False)
    order_id=db.Column('order_id', db.String(36), nullable=False)
    distance=db.Column('distance', db.Float, nullable=False)
    assigned_at=db.Column('assigned_at', db.String(30), nullable=False)
    picked_at=db.Column('picked_at', db.String(30), nullable=False)
    delivered_at=db.Column('delivered_at', db.String(30), nullable=False)

    courier = db.relationship('Courier', backref=db.backref('trips', lazy=True))

    def __init__(self, id, courier_id, order_id, distance, assigned_at, picked_at, delivered_at):
        self.id=id
        self.courier_id=courier_id
        self.order_id=order_id
        self.distance=distance
        self.assigned_at=assigned_at
        self.picked_at=picked_at
        self.delivered_at=delivered_at

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
            "deliveredAt": self.delivered_at
        }
        return data