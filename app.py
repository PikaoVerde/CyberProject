from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_googlemaps import GoogleMaps
from datetime import datetime
import os

app = Flask(__name__)

IMG_FOLDER = os.path.join('static', 'IMG')

app.config['UPLOAD_FOLDER'] = IMG_FOLDER

app.secret_key = "PikaoVerde"
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config['GOOGLEMAPS_KEY'] = "AIzaSyCGPs81uXNmtO-twbZR9oIKqzG8JzEjtzs"
#
GoogleMaps(app)

# GoogleMaps(app, key="AIzaSyCel7fvMD4zIoqDyfKCDxlEwUA-ns6SogM")


db = SQLAlchemy(app)


class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(100))

    def __init__(self, name, email, phone):
        self.name = name
        self.email = email
        self.phone = phone


class Markers(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    lat = db.Column(db.String(100))
    lng = db.Column(db.String(100))
    title = db.Column(db.String(100))
    creator = db.Column(db.String(100))
    creation = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, lat, lng, title, creator):
        self.lat = lat
        self.lng = lng
        self.title = title
        self.creator = creator


@app.route("/")
def home():

    return render_template("index.html")

@app.route("/login/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["nm"]
        session["user"] = user

        found_user = users.query.filter_by(name=user).first()
        if found_user:
            session["email"] = found_user.email
            session["phone"] = found_user.phone


        else:
            usr = users(user, "", "")
            db.session.add(usr)
            db.session.commit()

        flash("Login successfull!", "info")
        return redirect(url_for("user"))
    else:
        if "user" in session:
            return redirect(url_for("user"))
        return render_template("login.html")


@app.route("/user/", methods=["POST", "GET"])
def user():
    email = None
    phone = None
    if "user" in session:
        user = session["user"]

        if request.method == "POST":
            email = request.form["email"]
            phone = request.form["phone"]
            session["phone"] = phone
            session["email"] = email
            found_user = users.query.filter_by(name=user).first()
            found_user.email = email
            found_user.phone = phone
            db.session.commit()
            flash ("Information saved!", "info")
        else:
            if "email" in session:
                email = session["email"]
            if "phone" in session:
                phone = session["phone"]
        return render_template("user.html", email=email, user=user, phone=phone)
    else:
        return redirect(url_for("login"))


@app.route("/logout/")
def logout():
    if "user" in session:
        flash("Logged out successfully!", "info")
    session.pop("user", None)
    session.pop("email", None)
    session.pop("phone", None)
    return redirect(url_for("login"))

@app.route("/report", methods=["POST", "GET"])
def report():
    if "user" in session:
        user = session["user"]
        if request.method == "POST":
            description = request.form["des"]
            lat = request.form["la"]
            lng = request.form["ln"]
            mr = Markers(lat, lng, description, user)
            db.session.add(mr)
            db.session.commit()
            flash("Information saved! Thanks for the report", "info")
            return render_template("report.html")
        else:
            return render_template("report.html")
    else:
        return redirect(url_for("login"))

@app.route("/map")
def map():
    return render_template("map.html")

@app.route("/mapdata")
def mapdata():
    data = {
          "markers": []
    }

    markers = Markers.query.all()

    for mark in markers:
        mrkDate = mark.creation
        now = datetime.now()
        delta = now - mrkDate
        if delta.days > 1:
            # num = mark._id
            Markers.query.filter_by(creation=mrkDate).delete()
            db.session.commit()

    markers = Markers.query.all()

    for mrk in markers:
        marker_info = [{"lat": float(mrk.lat), "lng": float(mrk.lng)}, mrk.title]
        data["markers"].append(marker_info)

    return data

@app.route("/feed")
def feed():

    markers = Markers.query.all()

    for mark in markers:
        mrkDate = mark.creation
        now = datetime.now()
        delta = now - mrkDate
        if delta.days > 1:
            # num = mark._id
            Markers.query.filter_by(creation=mrkDate).delete()
            db.session.commit()

    markers = Markers.query.order_by(Markers.creation).all()
    print(markers)
    return render_template("feed.html", feedData=markers)


with app.app_context():
    db.create_all()
    app.run(debug=True)


