from datetime import datetime
import requests
from flaskr.producer import Producer

AVAILABLE_TAGS = ["fragile", "dangerous"]

# Retrieves current timestamp
def timestamp():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]


# Inserts object into database
def insert_into_db(obj, db):
    try:
        db.session.add(obj)
    except:
        db.session.rollback()
        raise
    else:
        db.session.commit()


# Clears session data
def clear_session(session):
    for key in [key for key in session]:
        session.pop(key, None)


# Requests orders
def get_orders(**params):
    try:
        return requests.get("http://localhost:5000/orders", params).json()
    except:
        return None


# Sends message to kafka
def message_kafka(topic, data):
    Producer().produce(topic, data)