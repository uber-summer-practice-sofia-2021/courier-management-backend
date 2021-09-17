from flask import (
    Blueprint,
    session,
    request,
    flash,
    redirect,
    url_for,
    render_template,
    jsonify,
)
from flask.globals import current_app
from flaskr.user.utils import *
from flaskr.database.models import *

user = Blueprint("user", __name__, url_prefix="/user")


@user.route("/pagination", methods=["GET"], defaults={"page": 1})
@user.route("/pagination/<int:page>", methods=["GET"])
def pagination(page):
    page = page
    per_page = 1
    trips = Trip.query.paginate(page, per_page, error_out=False)
    # print("Result......", users)
    return render_template("user/pagination.html", trips=trips)


# Login page
@user.route("/login", methods=["POST", "GET"])
def login():

    found_user = Courier.query.filter_by(id=session.get("id")).first()

    if found_user:
        flash("Already logged in!")
        return redirect(url_for("user.dashboard"))

    if request.method == "POST":
        email = request.form["email"].strip()

        insert_into_db(Courier(email), db)

        found_user = Courier.query.filter_by(email=email).first()

        session.permanent = True
        session["status"] = "inactive"
        session["id"] = found_user.id

        if found_user.current_order_id:
            flash("You have a trip in progress!")
            session["status"] = "active"
            return redirect(
                url_for("user.order_dashboard", orderID=found_user.current_order_id)
            )

        flash("Login successful!")
        return redirect(url_for("user.inactive"))

    return render_template("user/login.html")


# Endpoint for user settings page
@user.route("/settings", methods=["POST", "GET"])
def settings():
    found_user = Courier.query.filter_by(id=session.get("id")).first()

    if not found_user:
        flash("Invalid user or session expired!")
        return redirect(url_for("user.logout"))

    if found_user.current_order_id:
        flash("You have a trip in progress!")
        return redirect(url_for("user.dashboard", orderID=found_user.current_order_id))

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
        return redirect(url_for("user.dashboard"))

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
    found_user = Courier.query.filter_by(id=session.get("id")).first()

    if found_user:
        flash(f"You have been logged out, {found_user.name}!", "info")

    clear_session(session)
    return redirect(url_for("user.login"))


# User is redirected here upon going inactive
@user.route("/inactive", methods=["GET", "POST"])
def inactive():
    found_user = Courier.query.filter_by(id=session.get("id")).first()

    if not found_user:
        flash("Invalid user or session expired!")
        return redirect(url_for("user.login"))

    if not found_user.is_validated:
        flash("You need to complete your profile first!")
        return redirect(url_for("user.settings"))

    if found_user.current_order_id:
        flash("You have a trip in progress!")
        return redirect(url_for("user.dashboard", orderID=found_user.current_order_id))

    if request.method == "POST":
        if request.form.get("submit") == "active":
            session["status"] = "active"
            return redirect(url_for("user.dashboard"))

    session["status"] = "inactive"

    return render_template("user/inactive.html", name=found_user.name)


# Endpoint for the user dashboard
@user.route("/dashboard", methods=["POST", "GET"])
def dashboard():
    found_user = Courier.query.filter_by(id=session.get("id")).first()

    if not found_user:
        flash("Invalid user or session expired!")
        return redirect(url_for("user.login"))

    if session["status"] == "inactive":
        flash("You are currently inactive!")
        return redirect(url_for("user.inactive"))

    if not found_user.is_validated:
        flash("You need to complete your profile first!")
        return redirect(url_for("user.settings"))

    if found_user.current_order_id:
        flash("You have a trip in progress!")

        return redirect(
            url_for("user.order_dashboard", orderID=found_user.current_order_id)
        )

    page = request.args.get("page") if request.args.get("page") else 1
    limit = 10

    # Request orders from order management
    orders = get_orders(
        maxWeight=found_user.max_weight,
        maxHeight=found_user.max_height,
        maxWidth=found_user.max_width,
        maxLength=found_user.max_length,
        tags=found_user.tags.split(","),
        page=page,
        limit=limit,
    )

    data = orders.get("data") if orders.get("data") else []
    pagination = orders.get("pagination")

    if not orders:
        flash("There was a problem!")

    return render_template(
        "user/dashboard.html", name=found_user.name, data=data, pagination=pagination
    )


# Endpoint for order status change
@user.route("/dashboard/<orderID>", methods=["GET", "POST"])
def order_dashboard(orderID):
    found_user = Courier.query.filter_by(id=session.get("id")).first()

    if not found_user:
        flash("Invalid user or session expired!")
        return redirect(url_for("user.login"))

    if session["status"] == "inactive":
        flash("You are currently inactive!")
        return redirect(url_for("user.inactive"))

    if not found_user.is_validated:
        flash("You need to complete your profile first!")
        return redirect(url_for("user.settings"))

    if found_user.current_order_id and found_user.current_order_id != orderID:
        flash("You are already assigned an order!")
        return redirect(
            url_for("user.order_dashboard", orderID=found_user.current_order_id)
        )

    # Check if order was not open or there is already a trip for this order
    trips = Trip.query.filter(
        (Trip.order_id == orderID)
        & ((Trip.status != "CANCELLED") & (Trip.courier_id != found_user.id))
    ).all()
    order = get_order_by_id(orderID)
    if (
        not order
        or (order.get("status") != "OPEN" and not found_user.current_order_id)
        or trips
    ):
        flash("Order was already taken or cancelled!")
        found_user.current_order_id = None
        return redirect(url_for("user.dashboard"))

    # Get requested trip status
    status = request.form.get("status")
    if status:
        change_order_status(orderID, status)
    status = change_trip_status(status, found_user, orderID)

    return render_template("user/order.html", order=order, status=status)


@user.route("/history")
def history():

    found_user = Courier.query.filter_by(id=session.get("id")).first()

    if not found_user:
        flash("Invalid user or session expired!")
        return redirect(url_for("user.login"))

    if not found_user.is_validated:
        flash("You need to complete your profile first!")
        return redirect(url_for("user.settings"))

    if found_user.current_order_id:
        flash("You have a trip in progress!")

        return redirect(
            url_for("user.order_dashboard", orderID=found_user.current_order_id)
        )

    limit = 1
    older_than = request.args.get("older_than")
    newer_than = request.args.get("newer_than")

    # Get paginated history
    history = paginate(found_user.id, older_than, newer_than, limit + 1)
    # Remove first or last element based on action
    history = (
        (history[1:] if newer_than else history[:-1])
        if len(history) > limit
        else history
    )

    # Check buttons availability
    older = (older_than and len(history) > limit) or (
        history
        and len(paginate(found_user.id, history[-1].get("sorter"), None, limit + 1)) > 0
    )
    newer = (newer_than and len(history) > limit) or (
        history
        and len(paginate(found_user.id, None, history[0].get("sorter"), limit + 1)) > 0
    )

    return render_template("user/history.html", items=history, older=older, newer=newer)
