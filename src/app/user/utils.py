from datetime import datetime
from app.producer import Producer
from app.db.models import *
from flask import current_app, g
import requests, os, inspect as ins
from sqlalchemy import exc


AVAILABLE_TAGS = ["FRAGILE", "DANGEROUS"]
AVAILABLE_TRIP_STATES = ["ASSIGNED", "PICKED_UP", "COMPLETED", "CANCELLED"]


# Retrieves current timestamp
def timestamp():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]


# Inserts object into db
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
        return requests.post(
            f"http://{os.getenv('ORDER_MANAGEMENT_HOST')}:{os.getenv('ORDER_MANAGEMENT_PORT')}/orders/{orderID}?status={status.upper()}"
        )
    except Exception as e:
        current_app.logger.error(
            f"{e} -> {ins.getframeinfo(ins.currentframe()).function}"
        )
        return None


# Checks if order was not open or there is already a trip for this order
def check_order_availability(orderID):
    trips = Trip.query.filter(
        (Trip.order_id == orderID) & (Trip.status != "CANCELLED")
    ).all()
    order = get_order_by_id(orderID)

    if (
        not order
        or (order.get("status") != "OPEN" and not g.user.current_trip_id)
        or trips
    ):
        return False
    return True


# Initialize trip upon order assignment
def init_trip(courier, orderID):
    try:
        trip = Trip(courier.id, orderID)
        insert_into_db(trip, db)
        courier.current_trip_id = trip.id
        return db.session.commit()
    except exc.IntegrityError as e:
        current_app.logger.error(
            f"{e} -> {ins.getframeinfo(ins.currentframe()).function}"
        )
        db.session.rollback()


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
def change_trip_status(status, found_user, trip):
    try:
        if status not in AVAILABLE_TRIP_STATES:
            return trip.status

        # Set trip corresponding timestamp
        setattr(trip, status.lower() + "_at", timestamp())
        trip.status = status

        if status == "COMPLETED" or status == "CANCELLED":
            # Clear user current order id and msg kafka
            trip.sorter = getattr(trip, status.lower() + "_at") + trip.id
            found_user.current_trip_id = None
            message_kafka(
                os.environ["KAFKA_TOPIC"], trip.get_id()
            ) if status == "COMPLETED" else None

        db.session.commit()
        return status

    except Exception as e:
        current_app.logger.error(
            f"{e} -> {ins.getframeinfo(ins.currentframe()).function}"
        )
        return None