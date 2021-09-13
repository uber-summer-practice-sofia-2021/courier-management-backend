from flask import Blueprint, session, request, flash, redirect, url_for, render_template, json
from flaskr.user.utils import *
from flaskr.database.models import *

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
        # return redirect(url_for("user.dashboard"))

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
    orders = get_orders()
    data = orders.get("data")
    pagination = orders.get("pagination")

    if request.method == "POST":
        if request.form["submit_button"] == "Go inactive":
            session["status"] = "inactive"
            return redirect(url_for("user.inactive"))

    return render_template("user/dashboard.html", name=found_user.name, data=data)


# Endpoint for order visualization
@user.route("/dashboard/<orderID>", methods=["GET"])
def order_dashboard(orderID):
    found_user = Courier.query.filter_by(email=session.get("email")).first()

    if not found_user:
        flash("Invalid user or session expired!")
        return redirect(url_for("user.login"))

    insert_into_db(Trip(found_user.id, orderID), db)
    change_order_status(orderID, "assigned")

    fixtures_path = "../fixtures/orders.json"
    file = open(fixtures_path)
    data = json.load(file)
    file.close()
    input = next(item for item in data['data'] if item["ID"]==orderID)

    return render_template("user/order.html", orderID=orderID, input=input)


# Endpoint for order status change
@user.route("/dashboard/<orderID>/<status>", methods=["POST"])
def change_order_status(orderID, status):
    trip = Trip.query.filter_by(order_id=orderID).first()

    if status == "assigned":
        # send status change request to order management
        trip.assigned_at = timestamp()
    elif status == "picked":
        # send status change request to order management
        trip.picked_at = timestamp()
    elif status == "delivered":
        # send status change request to order management
        trip.delivered_at = timestamp()
        message_kafka("trips", trip.map())

    db.session.commit()
    return trip.map()
