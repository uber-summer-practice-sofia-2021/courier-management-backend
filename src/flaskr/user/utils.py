from datetime import datetime
from threading import current_thread
from flask.cli import with_appcontext
import requests
from flaskr.producer import Producer
from flaskr.database.models import db, Trip
from flask import current_app

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
        return {}


# Requests order by id
def get_order_by_id(orderID):
    try:
        return requests.get(f"http://localhost:5000/orders/{orderID}").json()
    except:
        return {}


# Send order status change
def change_order_status(orderID, status):
    try:
        requests.post(f"http://ordermanagement/orders/{orderID}?status={status.upper()}")
    except Exception as e:
        current_app.logger.debug(e)


# Sends message to kafka
def message_kafka(topic, data):
    try:
        Producer().produce(topic, data)
    except Exception as e:
        current_app.logger.debug(e)


# def get_before(courier_id, cursor, limit = 10):
#     try:
#         with current_app.app_context():
#             cursor = Trip.query.order_by(Trip.sorter.desc()).limit(limit).order_by(Trip.sorter).sorter if not cursor else cursor

#             results = db.session.execute(
#                 f"SELECT *\
#                 FROM (SELECT *\
#                     FROM Trips\
#                     WHERE courier_id LIKE '{courier_id}'\
#                         AND sorter NOT NULL AND sorter > '{cursor}'\
#                     ORDER BY sorter ASC\
#                     LIMIT {limit}) x\
#                 ORDER BY sorter DESC;"
#             )

#             return [list(x) for x in (results if results else [])]
#     except Exception as e:
#         current_app.logger.debug(e)
#         return None


# def get_after(courier_id, older_than, newer_than, limit = 10):
#     try:
#         with current_app.app_context():
#             cursor = Trip.query.order_by(Trip.sorter.desc()).first().sorter if not cursor else cursor

#             if not inc:
#                 results = db.session.execute(
#                     f"SELECT *\
#                     FROM Trip\
#                     WHERE courier_id LIKE '{courier_id}'\
#                         AND sorter NOT NULL AND sorter < '{cursor}'\
#                     ORDER BY sorter DESC\
#                     LIMIT {limit}"
#                 )
#             else:
#                 results = db.session.execute(
#                     f"SELECT *\
#                     FROM Trip\
#                     WHERE courier_id LIKE '{courier_id}'\
#                         AND sorter NOT NULL AND sorter <= '{cursor}'\
#                     ORDER BY sorter DESC\
#                     LIMIT {limit}"
#                 )

#             return [list(x) for x in (results if results else [])]
#     except Exception as e:
#         current_app.logger.debug(e)
#         return None


def paginate(courier_id, older_than, newer_than, limit = 10):
    try:
        with current_app.app_context():
            if older_than:
                results = db.session.execute(
                    f"SELECT *\
                    FROM Trip\
                    WHERE courier_id LIKE '{courier_id}'\
                        AND sorter NOT NULL AND sorter < '{older_than}'\
                    ORDER BY sorter DESC\
                    LIMIT {limit}"
                )
            else:
                results = db.session.execute(
                    f"SELECT *\
                    FROM Trip\
                    WHERE courier_id LIKE '{courier_id}'\
                        AND sorter NOT NULL AND sorter > '{newer_than}'\
                    ORDER BY sorter DESC\
                    LIMIT {limit}"
                )

            return [list(x) for x in (results if results else [])]
    except Exception as e:
        current_app.logger.debug(e)
        return None