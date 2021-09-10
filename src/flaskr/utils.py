from datetime import datetime

# Retrieves current timestamp
def timestamp():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

def insert_courier(courier, db):
    db.session.add(courier)
    db.session.commit()

def insert_trip(trip, db):
    db.session.add(trip)
    db.session.commit()