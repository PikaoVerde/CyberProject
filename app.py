from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_googlemaps import GoogleMaps, Map

app = Flask(__name__)
app.secret_key = "PikaoVerde"
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config['GOOGLEMAPS_KEY'] = "AIzaSyCel7fvMD4zIoqDyfKCDxlEwUA-ns6SogM"
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


@app.route("/")
def home():
    mymap = Map(
        identifier="mymap",
        lat=37.4419,
        lng=-122.1419,
        markers=[
            {
                'icon': 'http://maps.google.com/mapfiles/kml/shapes/caution.png',
                'lat': 37.4419,
                'lng': -122.1419,
                'infobox': "<b>Hello World</b>"
            },
            {
                'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
                'lat': 37.4300,
                'lng': -122.1400,
                'infobox': "<b>Hello World from other place</b>"
            }
        ]
    )
    return render_template("index.html", mymap=mymap)

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
    return redirect(url_for("login"))

@app.route("/map")
def map():
    return render_template("map.html")


with app.app_context():
    db.create_all()
    app.run(debug=True)


