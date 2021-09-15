from flask import (
    Blueprint,
    session,
    request,
    flash,
    redirect,
    url_for,
    render_template,
    json,
)
from flaskr.user.utils import *
from flaskr.database.models import *
import numpy as np
import pandas as pd
user = Blueprint("user", __name__, url_prefix="/user")


# Login page
@user.route("/login", methods=["POST", "GET"])
def login():

    found_user = Courier.query.filter_by(email=session.get("email")).first()

    if found_user:
        flash("Already logged in!")

        if found_user.is_validated:
            return redirect(url_for("user.dashboard"))
        return redirect(url_for("user.settings"))

    if request.method == "POST":
        email = request.form["email"].strip()

        if not Courier.query.filter_by(email=email).first():
            insert_into_db(Courier(email), db)

        found_user = Courier.query.filter_by(email=email).first()

        session.permanent = True
        session["status"] = "active"
        session["email"] = email

        flash("Login successful!")
        if found_user.is_validated:
            return redirect(url_for("user.dashboard"))
        return redirect(url_for("user.settings"))

    return render_template("user/login.html")


# Endpoint for user settings page
@user.route("/settings", methods=["POST", "GET"])
def settings():
    found_user = Courier.query.filter_by(email=session.get("email")).first()

    if not found_user:
        flash("Invalid user or session expired!")
        return redirect(url_for("user.logout"))

    if request.method == "POST":

        tags = request.form.getlist("tag-checkbox")
        found_user.name = request.form["name"].strip()
        found_user.max_weight = request.form["weight"]
        found_user.max_width = request.form["width"]
        found_user.max_height = request.form["height"]
        found_user.max_length = request.form["length"]
        found_user.tags = ",".join(tags) if tags else ""
        found_user.is_validated = True
        db.session.commit()

        flash("Information was saved!")

    return render_template(
        "user/settings.html",
        name=found_user.name,
        max_weight=found_user.max_weight,
        max_width=found_user.max_width,
        max_height=found_user.max_height,
        max_length=found_user.max_length,
        tags=[x for x in found_user.tags.split(",") if x],
        available_tags=AVAILABLE_TAGS,
    )


# Endpoint for user logout
@user.route("/logout")
def logout():
    found_user = Courier.query.filter_by(email=session.get("email")).first()

    if found_user:
        flash(f"You have been logged out, {found_user.name}!", "info")

    clear_session(session)
    return redirect(url_for("user.login"))


# User is redirected here upon going inactive
@user.route("/inactive", methods=["GET", "POST"])
def inactive():
    found_user = Courier.query.filter_by(email=session.get("email")).first()

    if not found_user:
        flash("Invalid user or session expired!")
        return redirect(url_for("user.login"))

    if request.method == "POST":
        if request.form["submit_button"] == "Go active":
            session["status"] = "active"
            return redirect(url_for("user.dashboard"))

    return render_template("user/inactive.html", name=found_user.name)


# Endpoint for the user dashboard
@user.route("/dashboard", methods=["POST", "GET"])
def dashboard():
    found_user = Courier.query.filter_by(email=session.get("email")).first()

    if not found_user:
        flash("Invalid user or session expired!")
        return redirect(url_for("user.login"))

    if session["status"] == "inactive":
        flash("You are currently inactive!")
        return redirect(url_for("user.inactive"))

    if not found_user.is_validated:
        flash("You need to complete your profile first!")
        return redirect(url_for("user.settings"))

    # Request orders from order management
    orders = get_orders(
        maxWeight=found_user.max_weight,
        maxHeight=found_user.max_height,
        maxWidth=found_user.max_width,
        maxLength=found_user.max_length,
        tags=found_user.tags.split(","),
    )

    data = orders.get("data")
    pagination = orders.get("pagination")

    if request.method == "POST":
        if request.form["submit_button"] == "Go inactive":
            session["status"] = "inactive"
            return redirect(url_for("user.inactive"))

    return render_template("user/dashboard.html", name=found_user.name, data=data)


# Endpoint for order status change
@user.route("/dashboard/<orderID>", methods=["POST"])
def change_order_status(orderID):

    found_user = Courier.query.filter_by(email=session.get("email")).first()
    if not found_user:
        flash("Invalid user or session expired!")
        return redirect(url_for("user.login"))

    status = request.args["status"]
    trip = Trip.query.filter_by(order_id=orderID).first()

    if status == "assigned":
        if trip:
            flash("Order is already taken")
            return redirect(url_for("user.dashboard"))

        # send status change request to order management
        #requests.post('http://localhost:5000/orders/orderID',status=ASSINGED)
        insert_into_db(Trip(found_user.id, orderID), db)
        trip = Trip.query.filter_by(order_id=orderID).first()
        trip.assigned_at = timestamp()
    elif status == "picked":
        # send status change request to order management
        #requests.post('http://localhost:5000/orders/orderID',status=PICKED)
        trip.picked_at = timestamp()
    elif status == "delivered":
        # send status change request to order management
        #requests.post('http://localhost:5000/orders/orderID',status=DELIVERED)
        trip.delivered_at = timestamp()
        message_kafka("trips", trip.map())
    db.session.commit()

    order = requests.get(f"http://localhost:5000/orders/{orderID}").json()

    return render_template("user/order.html", order=order)

# Creating an endpoint for the history of the courier
#In case the courier is not logged in - gets redirected to the loginpage
@user.route("/history")
def return_trips_history():
    if "email" not in session:
        return redirect(url_for("user.login"))

    found_user = Courier.query.filter_by(email=session["email"]).first()
    print(session["email"])
    print(found_user.id)
    history = Trip.query.filter_by(courier_id = found_user.id).all()
    print(history)
    print(history[0].array())
    for i in range(len(history)):
        history[i] = history[i].array()
    print(history)
    return render_template('user/history.html', items=history)
