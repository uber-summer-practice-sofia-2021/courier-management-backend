from flask import (
    Blueprint,
    session,
    request,
    flash,
    redirect,
    url_for,
    render_template,
)
from flask.globals import current_app
from app.user.utils import *
from app.db.models import *

user = Blueprint("user", __name__, url_prefix="/user")


@user.before_request
def load_user():
    g.user = Courier.query.filter_by(id=session.get("id")).first()


# Login page
@user.route("/login", methods=["POST", "GET"])
def login():

    if g.user:
        flash("Already logged in!")
        return redirect(url_for("user.dashboard"))

    if request.method == "POST":
        email = request.form["email"].strip()

        insert_into_db(Courier(email), db)

        g.user = Courier.query.filter_by(email=email).first()

        session.permanent = True
        session["status"] = "inactive"
        session["id"] = g.user.id

        if g.user.current_trip_id:
            flash("You have a trip in progress!")
            session["status"] = "active"
            return redirect(
                url_for("user.trip_dashboard", tripID=g.user.current_trip_id)
            )

        flash("Login successful!")
        return redirect(url_for("user.inactive"))

    return render_template("user/login.html")


# Endpoint for user settings page
@user.route("/settings", methods=["POST", "GET"])
def settings():

    if not g.user:
        flash("Invalid user or session expired!")
        return redirect(url_for("user.logout"))

    if g.user.current_trip_id:
        flash("You have a trip in progress!")
        return redirect(url_for("user.dashboard", tripID=g.user.current_trip_id))

    if request.method == "POST":

        tags = request.form.getlist("tag-checkbox")
        g.user.name = request.form["name"].strip()
        g.user.max_weight = request.form["weight"]
        g.user.max_width = request.form["width"]
        g.user.max_height = request.form["height"]
        g.user.max_length = request.form["length"]
        g.user.tags = ",".join(tags) if tags else ""
        g.user.is_validated = True
        db.session.commit()

        flash("Information was saved!")
        return redirect(url_for("user.dashboard"))

    return render_template(
        "user/settings.html",
        name=g.user.name,
        max_weight=g.user.max_weight,
        max_width=g.user.max_width,
        max_height=g.user.max_height,
        max_length=g.user.max_length,
        tags=[x for x in g.user.tags.split(",") if x],
        available_tags=AVAILABLE_TAGS,
    )


# Endpoint for user logout
@user.route("/logout")
def logout():

    if g.user:
        name = g.user.name

    clear_session(session)
    flash(f"You have been logged out, {name}!", "info")
    
    return redirect(url_for("user.login"))


# User is redirected here upon going inactive
@user.route("/inactive", methods=["GET", "POST"])
def inactive():

    if not g.user:
        flash("Invalid user or session expired!")
        return redirect(url_for("user.login"))

    if not g.user.is_validated:
        flash("You need to complete your profile first!")
        return redirect(url_for("user.settings"))

    if g.user.current_trip_id:
        flash("You have a trip in progress!")
        return redirect(url_for("user.trip_dashboard", tripID=g.user.current_trip_id))

    if request.method == "POST":
        if request.form.get("submit") == "active":
            session["status"] = "active"
            return redirect(url_for("user.dashboard"))

    session["status"] = "inactive"

    return render_template("user/inactive.html", name=g.user.name)


# Endpoint for the user dashboard
@user.route("/dashboard", methods=["POST", "GET"])
def dashboard():

    if not g.user:
        flash("Invalid user or session expired!")
        return redirect(url_for("user.login"))

    if session["status"] == "inactive":
        flash("You are currently inactive!")
        return redirect(url_for("user.inactive"))

    if not g.user.is_validated:
        flash("You need to complete your profile first!")
        return redirect(url_for("user.settings"))

    if g.user.current_trip_id:
        flash("You have a trip in progress!")

        return redirect(url_for("user.trip_dashboard", tripID=g.user.current_trip_id))

    if request.method == "POST":
        orderID = request.args.get("orderID")
        distance = request.args.get("distance")
        
        if not check_order_availability(orderID):
            flash("Order was already taken, completed or cancelled!")
            return redirect(url_for("user.dashboard"))

        init_trip(g.user, orderID, distance)

        return redirect(url_for("user.trip_dashboard", tripID=g.user.current_trip_id, status="ASSIGNED"))

    page = int(request.args.get("page")) if request.args.get("page") else 1

    # Request orders from order management
    orders = get_orders(
        maxWeight=g.user.max_weight,
        maxHeight=g.user.max_height,
        maxWidth=g.user.max_width,
        maxLength=g.user.max_length,
        tags=g.user.tags.split(","),
        page=page-1,
    )

    data = orders.get("data") if orders.get("data") else []
    pagination = orders.get("pagination")

    for order in data:
        order['distance'] = round(haversine_distance(order['from']['latitude'], order['from']['longitude'], order['to']['latitude'], order['to']['longitude']), 2)

    if not orders:
        flash("There was a problem!")

    return render_template(
        "user/dashboard.html", name=g.user.name, data=data, pagination=pagination
    )


# Endpoint for order status change
@user.route("/dashboard/<tripID>", methods=["GET", "POST"])
def trip_dashboard(tripID):

    trip = Trip.query.filter_by(id=tripID).first_or_404()

    if not g.user:
        flash("Invalid user or session expired!")
        return redirect(url_for("user.login"))

    if not g.user.is_validated:
        flash("You need to complete your profile first!")
        return redirect(url_for("user.settings"))

    if g.user.current_trip_id and tripID != g.user.current_trip_id:
        flash("You have a trip in progress!")
        return redirect(url_for("user.trip_dashboard", tripID=g.user.current_trip_id))

    order = get_order_by_id(trip.order_id)

    # Get requested trip status
    if request.method == "POST":
        status = request.args.get("status")

        if (trip.status == "ASSIGNED" and status in ["CANCELLED", "PICKED_UP"]) or (trip.status == "PICKED_UP" and status == "COMPLETED"):
            if status:
                current_app.logger.debug(status)
                change_order_status(trip.order_id, status)
            status = change_trip_status(status, g.user, trip)
        else:
            flash("Invalid operation!")

    return render_template("user/order.html", order=order, trip=trip)


@user.route("/history")
def history():

    if not g.user:
        flash("Invalid user or session expired!")
        return redirect(url_for("user.login"))

    if not g.user.is_validated:
        flash("You need to complete your profile first!")
        return redirect(url_for("user.settings"))

    if g.user.current_trip_id:
        flash("You have a trip in progress!")
        return redirect(url_for("user.trip_dashboard", tripID=g.user.current_trip_id))

    limit = 5
    older_than = request.args.get("older_than")
    newer_than = request.args.get("newer_than")

    # Get paginated history
    history = paginate(g.user.id, older_than, newer_than, limit + 1)
    # Remove first or last element based on action
    history = (
        (history[1:] if newer_than else history[:-1])
        if len(history) > limit
        else history
    )

    # Check buttons availability
    older = (older_than and len(history) > limit) or (
        history
        and len(paginate(g.user.id, history[-1].get("sorter"), None, limit + 1)) > 0
    )
    newer = (newer_than and len(history) > limit) or (
        history
        and len(paginate(g.user.id, None, history[0].get("sorter"), limit + 1)) > 0
    )

    return render_template("user/history.html", items=history, older=older, newer=newer)
