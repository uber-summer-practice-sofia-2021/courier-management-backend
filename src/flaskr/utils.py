from datetime import datetime

available_tags = ["fragile", "dangerous"]

# Retrieves current timestamp
def timestamp():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]


# Inserts courier into database
def insert_courier(courier, db):
    db.session.add(courier)
    db.session.commit()


# Inserts trip into database
def insert_trip(trip, db):
    db.session.add(trip)
    db.session.commit()
