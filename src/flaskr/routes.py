from flaskr import app
from flaskr.models import *
from flask import render_template, request, session, flash, redirect, url_for

json_data = {
    "courier": {
        "id": "7f4dc6b6-f8ba-477b-8b21-25446c9c72b3",
        "email": "example@email.com",
        "maxDimmension": {
            "maxwidth": 30.00,
            "maxheight": 20.00,
            "maxlength": 20.00
        },
        "name": "Jhon Nash",
        "tags": [ "fragile", "dangerous" ],
        "isActive": True,
        "isAvailable": True  
    }
}

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

@app.route("/couriers/<string:ID>")
def get_courier_data(ID):
    return Courier.query.filter(ID).first()

@app.route("/trips/<string:ID>")
def get_courier_data(ID):
    return Trip.query.filter(ID).first()

# @app.route('/dashboard')
# def dashboard():
#     if inSession:
#         show-courier-dashboard
#     else:
#         redirect-to-login-page