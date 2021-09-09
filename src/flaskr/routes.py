from flaskr import app, db
from flaskr.models import *
<<<<<<< HEAD
from flask import render_template, request, session, flash, redirect, url_for, jsonify, make_response, Response, json
=======
from flaskr.producer import Producer
from flask import render_template, request, session, flash, redirect, url_for, jsonify, make_response
>>>>>>> bcbe6c3c2f2fea5df78a8df6a4b81d30ca4272af
import uuid

@app.route("/", methods=["GET", "POST"])
def home():
   return redirect(url_for("login"))
   

@app.route("/view")
def view():
    return render_template("view.html", values=Courier.query.all())

    
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
            usr = Courier(email)
            db.session.add(usr)
            db.session.commit()
        
        flash("Login successful!")
        return redirect(url_for("user"))
    else:
        if "Email" in session:
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
    tags=None

    if "Email" in session:
        email=session["Email"]
        found_user = Courier.query.filter_by(email=email).first()
        if found_user and found_user.is_validated:
            return redirect(url_for("active"))
        

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

            arr=request.form.getlist('mycheckbox')
            if arr:
                tags=','.join(arr)


            found_user.name = name
            found_user.max_weight = max_weight
            found_user.max_width = max_width
            found_user.max_height = max_height
            found_user.max_length = max_length
            found_user.tags=tags
            found_user.is_validated=True
            db.session.commit()

            # flash("Information was saved!")
            return redirect(url_for("active"))
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
    if "Email" in session:
        email=session["Email"]
        flash(f"You have been logged out, {email}!","info")
    for key in [key for key in session]:
        session.pop(key, None)
    return redirect(url_for("login"))


@app.route("/active",methods=["POST","GET"])
def active():
    found_user=None
    name=None

    fixtures_path = "../fixtures/orders.json"
    file = open(fixtures_path)
    data = json.load(file)
    file.close()
    # print(Response(json.dumps(data), mimetype='application/json'))
    # print(data)
    # for item in data:
    #     print(json.dumps(item))

    # return Response(json.dumps(data), mimetype='application/json')
    if "Email" in session:
        email=session["Email"]
        found_user = Courier.query.filter_by(email=email).first()
        name=found_user.name
        found_user.is_validated=True
        db.session.commit()
    else:
        return redirect(url_for("login"))

    if request.method=="POST":
        if  request.form['submit_button']=='Go inactive':
             return redirect(url_for("inactive"))
        elif request.form['submit_button']=='edit_details':
            found_user.is_validated=False
            db.session.commit()
            return redirect(url_for("user"))
    return render_template("active.html",name=name,data=data)

@app.route("/inactive",methods=["GET","POST"])
def inactive():
    found_user=None
    name=None
    if "Email" in session:
        email=session["Email"]
        found_user = Courier.query.filter_by(email=email).first()
        name=found_user.name
        found_user.is_validated=True
        db.session.commit()

    if request.method=="POST": 
        if request.form['submit_button']=='Go active':  
            return redirect(url_for("active"))
        elif request.form['submit_button']=='edit_details':
            found_user.is_validated=False
            db.session.commit()
            return redirect(url_for("user"))
    return render_template("inactive.html",name=name)


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

<<<<<<< HEAD

# @app.route("/user/orders", methods=['GET', 'POST'])
# def orders():
#     return render_template("orders.html")

# @app.route("/tags")
# def tags():
#     if request.method == "POST":
#         tags = request.form.getlist("tags")
#         print(tags)
#         return "OK"

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
=======
""" Endpoint for order visualization """
@app.route('/orders/<orderID>', methods=['GET'])
def order_dashboard(orderID):
    if "Email" not in session:
        return redirect(url_for('login'))
    return render_template('order.html', orderID=orderID)

""" Endpoint for order status change """
@app.route('/orders/<orderID>/<status>', methods=['POST'])
def change_order_status(orderID, status):
    return "test"
>>>>>>> bcbe6c3c2f2fea5df78a8df6a4b81d30ca4272af
