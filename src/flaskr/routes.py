from flaskr import app, db
from flaskr.database.models import *
from flaskr.producer import message_kafka
from flask import (
    render_template,
    request,
    session,
    flash,
    redirect,
    url_for,
    jsonify,
    make_response,
    json,
)
from flaskr.utils import (
    clear_session,
    insert_into_db,
    timestamp,
    AVAILABLE_TAGS,
)


# Handles nonexistent pages
@app.errorhandler(404)
def page_not_found(error):
    return render_template("page-not-found.html"), 404


# Home page
@app.route("/", methods=["GET"])
def home():
    return redirect(url_for("login"))


# For debug purposes
@app.route("/view")
def view():
    return render_template(
        "view.html", couriers=Courier.query.all(), trips=Trip.query.all()
    )


# Error page
@app.route("/error")
def error():
    app.logger.debug(request.args["error"])
    return render_template("error.html")


# Login page
@app.route("/login", methods=["POST", "GET"])
def login():

    if request.method == "POST":
        email = request.form["email"].strip()

        try:
            insert_into_db(Courier(email), db)
        except:
            pass

        found_user = Courier.query.filter_by(email=email).first()

        app.logger.debug("here")

        session.permanent = True
        session["status"] = "active"
        session["email"] = email

        flash("Login successful!")
        if found_user.is_validated:
            return redirect(url_for("user_dashboard"))
        return redirect(url_for("user_settings"))

    found_user = Courier.query.filter_by(email=session.get('email')).first()

    if found_user:
        flash("Already logged in!")

        if found_user.is_validated:
            return redirect(url_for("user_dashboard"))
        return redirect(url_for("user_settings"))

    return render_template("login.html")


# Endpoint for user settings page
@app.route("/user/settings", methods=["POST", "GET"])
def user_settings():
    found_user = Courier.query.filter_by(email=session.get('email')).first()

    if not found_user:
        flash("Invalid user or session expired!")
        return redirect(url_for("logout"))

    if request.method == "POST":

        tags = request.form.getlist("tag-checkbox")
        found_user.name = request.form["name"]
        found_user.max_weight = request.form["weight"]
        found_user.max_width = request.form["width"]
        found_user.max_height = request.form["height"]
        found_user.max_length = request.form["length"]
        found_user.tags = ",".join(tags) if tags else ""
        found_user.is_validated = True
        db.session.commit()

        flash("Information was saved!")

    return render_template(
        "user-settings.html",
        name=found_user.name,
        max_weight=found_user.max_weight,
        max_width=found_user.max_width,
        max_height=found_user.max_height,
        max_length=found_user.max_length,
        tags=[x for x in found_user.tags.split(",") if x],
        available_tags=AVAILABLE_TAGS,
    )


# Endpoint for user logout
@app.route("/logout")
def logout():
    found_user = Courier.query.filter_by(email=session.get('email')).first()

    if found_user:
        flash(f"You have been logged out, {found_user.name}!", "info")

    clear_session(session)
    return redirect(url_for("login"))


# Endpoint for the user dashboard
@app.route("/user/dashboard", methods=["POST", "GET"])
def user_dashboard():
    found_user = Courier.query.filter_by(email=session.get('email')).first()

    if not found_user:
        flash("Invalid user or session expired!")
        return redirect(url_for("login"))

    if session["status"] == "inactive":
        flash("You are currently inactive!")
        return redirect(url_for("user_inactive"))

    if not found_user.is_validated:
        flash("You need to complete your profile first!")
        return redirect(url_for("user_settings"))

    fixtures_path = "../fixtures/orders.json"
    file = open(fixtures_path)
    data = json.load(file)
    file.close()

    if request.method == "POST":
        if request.form["submit_button"] == "Go inactive":
            session["status"] = "inactive"
            return redirect(url_for("user_inactive"))

    return render_template("user-dashboard.html", name=found_user.name, data=data)


# User is redirected here upon going inactive
@app.route("/user/inactive", methods=["GET", "POST"])
def user_inactive():
    found_user = Courier.query.filter_by(email=session.get('email')).first()

    if not found_user:
        flash("Invalid user or session expired!")
        return redirect(url_for("login"))

    if request.method == "POST":
        if request.form["submit_button"] == "Go active":
            session["status"] = "active"
            return redirect(url_for("user_dashboard"))

    return render_template("user-inactive.html", name=found_user.name)


# Endpoint for requesting courier info
@app.route("/couriers", methods=["GET"])
def get_courier_info():
    try:
        courier_id = request.args["courierID"]
        courier = Courier.query.filter_by(id=courier_id).first().map()
        response = make_response(jsonify(courier))
        response.headers["Content-Type"] = "application/json"
        return response
    except:
        return jsonify(None), 204


# Endpoint for requesting trip info
@app.route("/trips", methods=["GET"])
def get_trip_info():
    try:
        trip_id = request.args["tripID"]
        trip = Trip.query.filter_by(id=trip_id).first().map()
        response = make_response(jsonify(trip))
        response.headers["Content-Type"] = "application/json"
        return response
    except:
        return jsonify(None), 204


# Endpoint for order visualization
@app.route("/user/dashboard/<orderID>", methods=["GET"])
def order_dashboard(orderID):
    found_user = Courier.query.filter_by(email=session.get('email')).first()

    if not found_user:
        flash("Invalid user or session expired!")
        return redirect(url_for("login"))

    try:
        insert_into_db(Trip(found_user.id, orderID), db)
        change_order_status(orderID, "assigned")

        fixtures_path = "../fixtures/orders.json"
        file = open(fixtures_path)
        data = json.load(file)
        file.close()
        input = None
        for item in data:
            if item["ID"] == orderID:
                input = item
                break

        return render_template("order.html", orderID=orderID, input=input)
    except Exception as err:
        return redirect(url_for("error", error=err))


# Endpoint for order status change
@app.route("/user/dashboard/<orderID>/<status>", methods=["POST"])
def change_order_status(orderID, status):
    try:
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
    except Exception as err:
        return redirect(url_for("error", error=err))
