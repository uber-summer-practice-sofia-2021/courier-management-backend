from flaskr import app, db
from flaskr.database
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
from flaskr.utils import insert_courier, insert_trip, timestamp
import requests


# Home page
@app.route("/", methods=["GET", "POST"])
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
    app.logger.debug(request.args['error'])
    return render_template("error.html")


# Login page
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        email = request.form["email"]
        session["email"] = email

        found_user = Courier.query.filter_by(email=email).first()
        if not found_user:
            insert_courier(Courier(email), db)

        flash("Login successful!")
        return redirect(url_for("user"))
    else:
        if "email" in session:
            flash("Already logged in!")
            return redirect(url_for("user"))
        return render_template("login.html")


@app.route("/user", methods=["POST", "GET"])
def user():

    name = None
    max_weight = None
    max_width = None
    max_height = None
    max_length = None
    tags=None
    f_checked=False
    d_checked=False

    if "email" in session:
        email = session["email"]
        found_user = Courier.query.filter_by(email=email).first()
        if found_user and found_user.is_validated:
            return redirect(url_for("active"))

        if request.method == "POST":

            name = request.form["name"]
            max_weight = request.form["weight"]
            max_width = request.form["width"]
            max_height = request.form["height"]
            max_length = request.form["length"]

            arr=request.form.getlist('mycheckbox1')
            if request.form.get('mycheckbox2'):
                arr.append(str(request.form.get('mycheckbox2')))
            
            if arr:
                tags=','.join(arr)
                      
            found_user.name = name
            found_user.max_weight = max_weight
            found_user.max_width = max_width
            found_user.max_height = max_height
            found_user.max_length = max_length
            found_user.tags = tags
            found_user.is_validated = True
            db.session.commit()

            # flash("Information was saved!")
            return redirect(url_for("active"))
        else:
            name = found_user.name 
            max_weight = found_user.max_weight 
            max_width = found_user.max_width
            max_height = found_user.max_height
            max_length = found_user.max_length

            if found_user.tags:
                tag_arr=found_user.tags.split(",")
                for t in tag_arr:
                    if t=='FRAGILE':
                        f_checked=True
                    elif t=='DANGEROUS':
                        d_checked=True

        return render_template(
            "user.html",
            name=name,
            max_weight=max_weight,
            max_width=max_width,
            max_height=max_height,
            max_length=max_length,
            f_checked=f_checked,
            d_checked=d_checked
        )
    else:
        flash("You are not logged in!")
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    if "email" in session:
        email = session["email"]
        flash(f"You have been logged out, {email}!", "info")
    for key in [key for key in session]:
        session.pop(key, None)
    return redirect(url_for("login"))


@app.route("/active", methods=["POST", "GET"])
def active():
    found_user = None
    name = None

    fixtures_path = "../fixtures/orders.json"
    file = open(fixtures_path)
    data = json.load(file)
    file.close()

    if "email" in session:
        email = session["email"]
        found_user = Courier.query.filter_by(email=email).first()
        name = found_user.name
        found_user.is_validated = True
        db.session.commit()
    else:
        return redirect(url_for("login"))

    if request.method == "POST":
        if request.form["submit_button"] == "Go inactive":
            return redirect(url_for("inactive"))
        elif request.form["submit_button"] == "edit_details":
            found_user.is_validated = False
            db.session.commit()
            return redirect(url_for("user"))

    return render_template("active.html", name=name, data=data)


@app.route("/inactive", methods=["GET", "POST"])
def inactive():
    found_user = None
    name = None
    if "email" in session:
        email = session["email"]
        found_user = Courier.query.filter_by(email=email).first()
        name = found_user.name
        found_user.is_validated = True
        db.session.commit()
    else:
        return redirect(url_for("login"))

    if request.method == "POST":
        if request.form["submit_button"] == "Go active":
            return redirect(url_for("active"))
        elif request.form["submit_button"] == "edit_details":
            found_user.is_validated = False
            db.session.commit()
            return redirect(url_for("user"))
    return render_template("inactive.html", name=name)


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
        return make_response(jsonify(None), 401)


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
        return make_response(jsonify(None), 401)


# Endpoint for order visualization
@app.route("/active/<orderID>", methods=["GET"])
def order_dashboard(orderID):
    if "email" not in session:
        return redirect(url_for("login"))

    try:
        found_user = Courier.query.filter_by(email=session["email"]).first()
        insert_trip(Trip(found_user.id, orderID), db)
        requests.post(f"http://localhost:5000/active/{orderID}/assigned")

        fixtures_path = "../fixtures/orders.json"
        file = open(fixtures_path)
        data = json.load(file)
        file.close()
        input=None
        for item in data:
            if item["ID"]==orderID:
                input=item
                break

        return render_template("order.html", orderID=orderID, input=input)
    except Exception as err:
        return redirect(url_for("error", error=err))

# Endpoint for order status change
@app.route("/active/<orderID>/<status>", methods=["POST"])
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
    except Exception as err:
        return redirect(url_for("error", error=err))