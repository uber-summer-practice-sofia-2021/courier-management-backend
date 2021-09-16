from re import I
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
import requests

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

    found_user = Courier.query.filter_by(email=session.get("email")).first()

    if found_user:
        flash("Already logged in!")
        return redirect(url_for("user.dashboard"))

    if request.method == "POST":
        email = request.form["email"].strip()

        if not Courier.query.filter_by(email=email).first():
            insert_into_db(Courier(email), db)

        found_user = Courier.query.filter_by(email=email).first()

        session.permanent = True
        session["status"] = "active"
        session["email"] = email

        flash("Login successful!")
        return redirect(url_for("user.dashboard"))

    return render_template("user/login.html")


# Endpoint for user settings page
@user.route("/settings", methods=["POST", "GET"])
def settings():
    found_user = Courier.query.filter_by(email=session.get("email")).first()

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

    return render_template("user/inactive.html", name=found_user.name)


# Endpoint for the user dashboard
@user.route("/dashboard", methods=["POST", "GET"])
def dashboard():
    page = request.args.get("page") if request.args.get("page") else 1
    limit = 10
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

    if found_user.current_order_id:
        flash("You have a trip in progress!")

        return redirect(
            url_for("user.order_dashboard", orderID=found_user.current_order_id)
        )

    if request.method == "POST":
        if request.form.get("submit") == "inactive":
            session["status"] = "inactive"
            return redirect(url_for("user.inactive"))

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

    if not orders:
        return render_template("errors/error")

    data = orders.get("data")
    pagination = orders.get("pagination")

    return render_template(
        "user/dashboard.html", name=found_user.name, data=data, pagination=pagination
    )


# Endpoint for order status change
@user.route("/dashboard/<orderID>", methods=["GET", "POST"])
def order_dashboard(orderID):
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

    if found_user.current_order_id and found_user.current_order_id != orderID:
        flash("You are already assigned an order!")
        return redirect(
            url_for("user.order_dashboard", orderID=found_user.current_order_id)
        )

    status = request.form.get("status")
    trip = Trip.query.filter_by(order_id=orderID).first()

    if status == "assigned":
        if trip:
            flash("Order is already taken")
            return redirect(url_for("user.dashboard"))

        insert_into_db(Trip(found_user.id, orderID), db)
        trip = Trip.query.filter_by(order_id=orderID).first()
        trip.assigned_at = timestamp()
        found_user.current_order_id = orderID
    elif status == "picked_up":
        trip.picked_at = timestamp()
    elif status == "completed":
        trip.delivered_at = timestamp()
        trip.sorter = trip.delivered_at + trip.id
        found_user.current_order_id = None
        message_kafka("trips", trip.map())
    db.session.commit()

    change_order_status(orderID, status)
    order = get_order_by_id(orderID)

<<<<<<< HEAD
    return render_template("user/boostrap_order.html", order=order,status=status)
=======
    return render_template("user/order.html", order=order, status=status)
>>>>>>> 06f1775a62db5d0332785bda4c154ce2a902c308


@user.route("/history")
def history():

    found_user = Courier.query.filter_by(email=session.get("email")).first()

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
    # next_cursor = request.args.get("next_cursor")
    # prev_cursor = request.args.get("prev_cursor")
    trip = Trip.query.order_by(Trip.sorter.desc()).first()
    cursors = [] + request.args.getlist("cursors")
    if not cursors:
        cursors.append(trip.sorter if trip else None)
    current_cursor = cursors[-1]
    action = request.args.get('action')

    # history = (
    #     Trip.query.filter_by(courier_id=found_user.id)
    #     .order_by(Trip.delivered_at.desc())
    #     .all()
    # )

    # if prev_cursor:
    #     print(prev_cursor)
    #     index = max(
    #         next(x for (x, e) in enumerate(history) if e.id == prev_cursor[0]) - 1, 0
    #     )
    #     next_cursor = [history[index].id, index]
    #     index1 = max(
    #         next(x for (x, e) in enumerate(history) if e.id == prev_cursor[0]) - limit,
    #         0,
    #     )
    #     prev_cursor = [history[index1].id, index1]
    # elif next_cursor:
    #     index = min(
    #         next(x for (x, e) in enumerate(history) if e.id == next_cursor[0]) + 1,
    #         len(history) - 1,
    #     )
    #     prev_cursor = [history[index].id, index]
    #     print(prev_cursor)
    #     index1 = min(
    #         next(x for (x, e) in enumerate(history) if e.id == next_cursor[0]) + limit,
    #         len(history) - 1,
    #     )
    #     next_cursor = [history[index1].id, index1]
    # else:
    #     if len(history) > 0:
    #         prev_cursor = [history[0].id, 0]
    #     if len(history) >= limit:
    #         next_cursor = [history[limit - 1].id, limit - 1]
    #     else:
    #         next_cursor = [history[-1].id, len(history) - 1]

    # history = history[int(prev_cursor[1]) : int(next_cursor[1]) + 1]

    #history = get_after(found_user.id, next_cursor, limit) if next_cursor else get_before(found_user.id, prev_cursor, limit)


    # history = get_after(found_user.id, next_cursor, limit, True if not next_cursor else False)
    # current_app.logger.debug(prev_cursor)

    # if not history:
    #     flash("You've reached the end of the list!")
    #     history = get_after(found_user.id, prev_cursor, limit, True)

    if action == 'prev':
        for i in range(2):
            if len(cursors)>1:
                cursors.pop()
        current_cursor = cursors[-1] if cursors else None
        history = get_after(found_user.id, current_cursor, limit, True if not len(cursors)>1 else False)
    else:
        history = get_after(found_user.id, current_cursor, limit, True if not len(cursors)>1 else False)

    if not history:
        current_app.logger.debug(history)
        flash("You've reached the end of the list!")
        if len(cursors)>1:
            cursors.pop()
        current_cursor = cursors[-1] if cursors else None
        history = get_after(found_user.id, current_cursor, limit, True if not len(cursors)>1 else False)


    return render_template(
        "user/history.html",
        items=history if history else [],
        # prev_cursor=history[0][7] if history else None,
        # next_cursor=history[-1][7] if history else None,
        cursors = cursors + ([history[-1][7]] if history else []),
    )
