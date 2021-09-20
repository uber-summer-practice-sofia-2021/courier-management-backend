from flask import Blueprint, render_template, redirect, url_for, json, current_app, session, g
from werkzeug.exceptions import HTTPException
from app.db.models import *

main = Blueprint("main", __name__)


# Exception handling
@main.app_errorhandler(HTTPException)
def handle_http_exception(e):
    try:
        return render_template(f"errors/{e.code}.html"), e.code
    except:
        response = e.get_response()
        response.data = json.dumps(
            {
                "code": e.code,
                "name": e.name,
                "description": e.description,
            }
        )
        response.content_type = "mainlication/json"
        return response


# Home page
@main.route("/")
def home():
    return redirect(url_for("user.login"))


# For debug purposes
@main.route("/view")
def view():
    return render_template(
        "view.html",
        couriers=Courier.query.all(),
        trips=Trip.query.all(),
        db_info=current_app.config.get("SQLALCHEMY_DATABASE_URI"),
    )
