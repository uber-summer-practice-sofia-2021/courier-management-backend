from flaskr import app
from flaskr.models import *
from flask import render_template, request, session, flash, redirect, url_for, jsonify, make_response

@app.route("/")
def home():
    return render_template("index.html")
    
@app.route("/login" , methods=["POST","GET"])
def login():
    if request.method == "POST":
        session.permanent=True
        user=request.form["nm"]
        session["user"]=user
        flash("Login successful!")
        return redirect(url_for("user"))
    else:
        if "user" in session:
            flash("Already logged in!")
            return redirect(url_for("user"))
        return render_template("login.html")

@app.route("/user",methods=["POST","GET"])
def user():
    email=None
    if "user" in session:
        user=session["user"]
        if request.method=="POST":
            email=request.form["email"]
            session["email"]=email
            flash("Email was saved!")
        else:
            if "email" in session:
                email=session["email"]

        return render_template("user.html",email=email)
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
@app.route("/couriers", methods=['GET'])
def get_courier_info():
    try:
        courier_id = request.args['courierID']
        courier = Courier.query.filter_by(id=courier_id).first().map()
        response = make_response(jsonify(courier))
        response.headers["Content-Type"] = "application/json"
        return response
    except:
        return make_response(jsonify(None), 401)

""" Endpoint for requesting trip info """
@app.route("/trips", methods=['GET'])
def get_trip_info():
    try:
        trip_id = request.args['tripID']
        trip = Trip.query.filter_by(id=trip_id).first().map()
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