from datetime import datetime
from threading import current_thread
from flask.cli import with_appcontext
import requests
from flaskr.producer import Producer
from flaskr.database.models import db, Trip
from flask import current_app
import os

AVAILABLE_TAGS = ["fragile", "dangerous"]


# Retrieves current timestamp
def timestamp():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]


# Inserts object into database
def insert_into_db(obj, db):
    try:
        db.session.add(obj)
    except Exception as e:
        current_app.logger.debug(e)
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
        return requests.get(f"http://{os.environ['ORDER_MANAGEMENT_HOST']}:{os.environ['ORDER_MANAGEMENT_PORT']}/orders", params).json()
    except Exception as e:
        current_app.logger.debug(e)
        return {}


# Requests order by id
def get_order_by_id(orderID):
    try:
        return requests.get(f"http://{os.environ['ORDER_MANAGEMENT_HOST']}:{os.environ['ORDER_MANAGEMENT_PORT']}/orders/{orderID}").json()
    except Exception as e:
        current_app.logger.debug(e)
        return {}


# Send order status change
def change_order_status(orderID, status):
    try:
        requests.post(f"http://{os.environ['ORDER_MANAGEMENT_HOST']}:{os.environ['ORDER_MANAGEMENT_PORT']}/orders/{orderID}?status={status.upper()}")
    except Exception as e:
        current_app.logger.debug(e)


# Sends message to kafka
def message_kafka(topic, data):
    try:
        Producer().produce(topic, data)
    except Exception as e:
        current_app.logger.debug(e)


# Provides a cursor based pagination
def paginate(courier_id, older_than, newer_than, limit = 10):
    try:
        with current_app.app_context():
            if newer_than:
                results = db.session.execute(
                    f"SELECT *\
                    FROM (SELECT *\
                        FROM Trip\
                        WHERE courier_id LIKE '{courier_id}'\
                            AND sorter NOT NULL AND sorter > '{newer_than}'\
                        ORDER BY sorter ASC\
                        LIMIT {limit}) x\
                    ORDER BY sorter DESC"
                )
            else:
                results = db.session.execute(
                    f"SELECT *\
                    FROM Trip\
                    WHERE courier_id LIKE '{courier_id}'\
                        AND sorter NOT NULL " +
                        (f"AND sorter < '{older_than}'" if older_than else "") +
                    f"ORDER BY sorter DESC\
                    LIMIT {limit}"
                )
            return [list(x) for x in (results if results else [])]
    except Exception as e:
        current_app.logger.debug(e)
        return None