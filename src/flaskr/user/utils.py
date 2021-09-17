from datetime import datetime

from werkzeug.utils import redirect
from flaskr.producer import Producer
from flaskr.database.models import *
from flask import current_app
import requests, os, inspect as ins
from sqlalchemy import exc


AVAILABLE_TAGS = ["FRAGILE", "DANGEROUS"]


# Retrieves current timestamp
def timestamp():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]


# Inserts object into database
def insert_into_db(obj, db):
    try:
        db.session.add(obj)
        return db.session.commit()
    except exc.IntegrityError as e:
        current_app.logger.error(
            f"{e} -> {ins.getframeinfo(ins.currentframe()).function}"
        )
        db.session.rollback()


# Clears session data
def clear_session(session):
    for key in [key for key in session]:
        session.pop(key, None)


# Requests orders
def get_orders(**params):
    try:
        return requests.get(
            f"http://{os.getenv('ORDER_MANAGEMENT_HOST')}:{os.getenv('ORDER_MANAGEMENT_PORT')}/orders",
            params,
        ).json()
    except Exception as e:
        current_app.logger.error(
            f"{e} -> {ins.getframeinfo(ins.currentframe()).function}"
        )
        return {}


# Requests order by id
def get_order_by_id(orderID):
    try:
        return requests.get(
            f"http://{os.getenv('ORDER_MANAGEMENT_HOST')}:{os.getenv('ORDER_MANAGEMENT_PORT')}/orders/{orderID}"
        ).json()
    except Exception as e:
        current_app.logger.info(
            f"http://{os.getenv('ORDER_MANAGEMENT_HOST')}:{os.getenv('ORDER_MANAGEMENT_PORT')}/orders/{orderID}"
        )
        current_app.logger.error(
            f"{e} -> {ins.getframeinfo(ins.currentframe()).function}"
        )
        return {}


# Send order status change
def change_order_status(orderID, status):
    try:
        requests.post(
            f"http://{os.getenv('ORDER_MANAGEMENT_HOST')}:{os.getenv('ORDER_MANAGEMENT_PORT')}/orders/{orderID}?status={status.upper()}"
        )
    except Exception as e:
        current_app.logger.error(
            f"{e} -> {ins.getframeinfo(ins.currentframe()).function}"
        )


# Sends message to kafka
def message_kafka(topic, data):
    try:
        Producer().produce(topic, data)
    except Exception as e:
        current_app.logger.error(
            f"{e} -> {ins.getframeinfo(ins.currentframe()).function}"
        )


# Provides a cursor based pagination
def paginate(courier_id, older_than, newer_than, limit=10):
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
                        AND sorter NOT NULL "
                    + (f"AND sorter < '{older_than}'" if older_than else "")
                    + f"ORDER BY sorter DESC\
                    LIMIT {limit}"
                )
            results = results.mappings().all()
            return [x for x in (results if results else [])]
    except Exception as e:
        current_app.logger.error(
            f"{e} -> {ins.getframeinfo(ins.currentframe()).function}"
        )
        return []


# Changes trip status and returns it's status
def change_trip_status(status, found_user, orderID):
    try:
        if status == "ASSIGNED":
            # Insert trip into database and set timestamp
            insert_into_db(Trip(found_user.id, orderID), db)
            found_user.current_order_id = orderID

        # Fetch trip from db
        trip = Trip.query.filter(
            Trip.order_id == orderID,
            Trip.courier_id == found_user.id,
            Trip.status != "CANCELLED",
        ).first()

        if not status:
            return trip.status

        # Set trip corresponding timestamp
        setattr(trip, status.lower() + "_at", timestamp())
        trip.status = status

        if status == "COMPLETED":
            # Clear user current order id and msg kafka
            trip.sorter = trip.completed_at + trip.id
            found_user.current_order_id = None
            message_kafka("trips", trip.get_id())

        db.session.commit()
        return status

    except Exception as e:
        current_app.logger.error(
            f"{e} -> {ins.getframeinfo(ins.currentframe()).function}"
        )
        return None
