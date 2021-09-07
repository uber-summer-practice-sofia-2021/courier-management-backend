from flaskr import app, db
from flaskr.models import *
from flask import render_template, request, session, flash, redirect, url_for, jsonify, make_response
from random import random

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/view")
def view():
    return render_template("view.html", values=Courier.query.all())

# @app.route("/tags")
# def tags():
#     if request.method == "POST":
#         tags = request.form.getlist("tags")
#         print(tags)
#         return "OK"
    
@app.route("/login" , methods=["POST","GET"])
def login():
    if request.method == "POST":
        session.permanent=True
        email = request.form["Email"]
        session["Email"] = email

        found_user = Courier.query.filter_by(email=email).first()
        if found_user:
            session["nm"] = found_user.name
            session["weight"] = found_user.max_weight
            session["width"] = found_user.max_width
            session["height"] = found_user.max_height
            session["length"] = found_user.max_length
        else:
            r = random()
            usr = Courier(id=str(r), email=email, name=None, max_weight = None, max_width=None, max_length=None, max_height=None, tags=None)
            db.session.add(usr)
            db.session.commit()
        
        flash("Login successful!")
        return redirect(url_for("user"))
    else:
        if "user" in session:
            flash("Already logged in!")
            return redirect(url_for("user"))
        return render_template("login.html")

@app.route("/user",methods=["POST","GET"])
def user():
    
    name = None
    max_weight = None
    max_width = None
    max_height = None
    max_length = None

    if "Email" in session:
        email=session["Email"]
        if request.method=="POST":

            name=request.form["nm"]
            session["nm"]=name

            max_weight=request.form["weight"]
            session["weight"]=max_weight

            max_width=request.form["width"]
            session["width"]=max_width

            max_height=request.form["height"]
            session["height"]=max_height

            max_length=request.form["length"]
            session["length"]=max_length

            found_user = Courier.query.filter_by(email=email).first()
            found_user.name = name
            found_user.max_weight = max_weight
            found_user.max_width = max_width
            found_user.max_height = max_height
            found_user.max_length = max_length
            db.session.commit()

            flash("Information was saved!")
        else:
            if "nm" in session and "weight" in session and "width" in session and "height" in session and "length" in session:
                name=session["nm"]
                max_weight=session["weight"]
                max_width=session["width"]
                max_height=session["height"]
                max_length=session["length"]

        return render_template("user.html", name=name, max_weight=max_weight, max_width=max_width, max_height=max_height, max_length=max_length)
    else:
        flash("You are not logged in!")
        return redirect(url_for("login"))
   
@app.route("/logout")
def logout():
    if "user" in session:
        user=session["user"]
        flash(f"You have been logged out!, {user}","info")
    session.pop("user",None)
    session.pop("email",None)
    return redirect(url_for("login"))

""" Endpoint for requesting courier info """
@app.route("/couriers", methods=['GET', 'POST'])
def get_courier_info():
    try:
        courier_id = request.json
        courier = Courier.query.filter_by(id=courier_id['courierID']).first().map()
        response = make_response(jsonify(courier))
        response.headers["Content-Type"] = "application/json"
        return response
    except:
        return make_response(jsonify(None), 401)

""" Endpoint for requesting trip info """
@app.route("/trips", methods=['GET', 'POST'])
def get_trip_info():
    try:
        trip_id = request.json
        trip = Trip.query.filter_by(id=trip_id['tripID']).first().map()
        response = make_response(jsonify(trip))
        response.headers["Content-Type"] = "application/json"
        return response
    except:
        return make_response(jsonify(None), 401)

# @app.route('/user/dashboard')
# def dashboard():
#     if inSession:
#         show-courier-dashboard
#     else:
#         redirect-to-login-page

# @app.route('/user/settings')
# def settings():
#     if inSession:
#         show-courier-settings
#     else:
#         redirect-to-login-page