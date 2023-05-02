from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_googlemaps import GoogleMaps
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

IMG_FOLDER = os.path.join('static', 'IMG')

app.config['UPLOAD_FOLDER'] = IMG_FOLDER

app.secret_key = "PikaoVerde"
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config['GOOGLEMAPS_KEY'] = "AIzaSyAAqWy0DmJhNoklNmZgyVRiZY9daxfswrY"
#
GoogleMaps(app)

# GoogleMaps(app, key="AIzaSyCel7fvMD4zIoqDyfKCDxlEwUA-ns6SogM")


db = SQLAlchemy(app)


class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    password_hash = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(100))

    @property
    def password(self):
        raise AttributeError('password in not a readable attribute')

    def verify_passwrord(self, password):
        return check_password_hash(self.password_hash, password)

    def __init__(self, name, password, email, phone):
        self.name = name
        self.password_hash = generate_password_hash(password)
        self.email = email
        self.phone = phone


class Markers(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    lat = db.Column(db.String(100))
    lng = db.Column(db.String(100))
    address = db.Column(db.String(100))
    title = db.Column(db.String(100))
    creator = db.Column(db.String(100))
    creation = db.Column(db.DateTime)
    active = db.Column(db.Integer())

    def __init__(self, lat, lng, add, title, creator, creation):
        self.lat = lat
        self.lng = lng
        self.address = add
        self.title = title
        self.creator = creator
        self.creation = creation
        self.active = 1


@app.route("/")
def home():

    return render_template("index.html")

@app.route("/login/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["nm"]
        password = request.form["pwrd"]
        session["user"] = user

        found_user = users.query.filter_by(name=user).first()
        if found_user and check_password_hash(found_user.password_hash, password):
            session["email"] = found_user.email
            session["phone"] = found_user.phone
            flash("Login successfull!", "info")

        elif found_user and check_password_hash(found_user.password_hash, password) == False:
            flash("Incorect password, Try again", "info")
            return render_template("login.html")

        else:
            usr = users(user,password, "", "")
            db.session.add(usr)
            db.session.commit()
            flash("Account created, Welcome", "info")

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

        if user == "Admin":
            if request.method == "POST":
                id = request.form["ide"]
                found_user = Markers.query.filter_by(_id=id).first()
                found_user.active = 0
                db.session.commit()

                markers = Markers.query.filter_by(active = 1)

                for mark in markers:
                    mrkDate = mark.creation
                    now = datetime.now()
                    delta = now - mrkDate
                    if delta.days >= 1:
                        # num = mark._id
                        found_user = Markers.query.filter_by(creation=mrkDate).first()
                        found_user.active = 0
                        db.session.commit()

                markers = Markers.query.filter_by(active = 1).order_by(Markers.creation).all()
                old = Markers.query.filter_by(active=0).order_by(Markers.creation).all()

                return render_template("user.html", user=user, feedData=markers, oldData=old)
            else:
                markers = Markers.query.filter_by(active = 1)

                for mark in markers:
                    mrkDate = mark.creation
                    now = datetime.now()
                    delta = now - mrkDate
                    if delta.days >= 1:
                        # num = mark._id
                        found_user = Markers.query.filter_by(creation=mrkDate).first()
                        found_user.active = 0
                        db.session.commit()

                markers = Markers.query.filter_by(active = 1).order_by(Markers.creation).all()
                old = Markers.query.filter_by(active=0).order_by(Markers.creation).all()

                return render_template("user.html", user=user, feedData=markers, oldData=old)

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
            add = request.form["adre"]
            # add = "test"
            lat = request.form["la"]
            lng = request.form["ln"]
            dtime = datetime.now()
            print(lat, lng)
            mr = Markers(lat, lng, add, description, user, dtime)
            db.session.add(mr)
            db.session.commit()
            flash("Information saved! Thanks for the report", "info")
            return render_template("report.html")
        else:
            return render_template("report.html")
    else:
        flash("First log in", "info")
        return redirect(url_for("login"))


@app.route("/map")
def map():
    return render_template("map.html")

@app.route("/mapdata")
def mapdata():
    data = {
          "markers": []
    }

    markers = Markers.query.filter_by(active = 1)

    for mark in markers:
        mrkDate = mark.creation
        now = datetime.now()
        delta = now - mrkDate
        if delta.days >= 1:
            # num = mark._id
            found_user = Markers.query.filter_by(creation=mrkDate).first()
            found_user.active = 0
            db.session.commit()

    markers = Markers.query.filter_by(active = 1)

    for mrk in markers:
        marker_info = [mrk.lat, mrk.lng, mrk.title]
        data["markers"].append(marker_info)

    return data

@app.route("/feed",  methods=["POST", "GET"])
def feed():
    if "user" in session:
        user = session["user"]
        if request.method == "POST":
            id = request.form["ide"]
            found_user = Markers.query.filter_by(_id=id).first()
            found_user.active = 0
            db.session.commit()

            markers = Markers.query.filter_by(active = 1)

            for mark in markers:
                mrkDate = mark.creation
                now = datetime.now()
                delta = now - mrkDate
                if delta.days >= 1:
                    # num = mark._id
                    found_user = Markers.query.filter_by(creation=mrkDate).first()
                    found_user.active = 0
                    db.session.commit()

            markers = Markers.query.filter_by(active = 1).order_by(Markers.creation).all()
            return render_template("feed.html", user=user, feedData=markers)
        else:


            markers = Markers.query.filter_by(active = 1)

            for mark in markers:
                mrkDate = mark.creation
                now = datetime.now()
                delta = now - mrkDate
                if delta.days >= 1:
                    # num = mark._id
                    found_user = Markers.query.filter_by(creation=mrkDate).first()
                    found_user.active = 0
                    db.session.commit()

            markers = Markers.query.filter_by(active = 1).order_by(Markers.creation).all()
            print(markers)
            return render_template("feed.html", user=user, feedData=markers)
    flash("First log in", "info")
    return redirect(url_for("login"))


with app.app_context():
    db.create_all()
    app.run(debug=True)


