from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "PikaoVerde"
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)


class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

    def __init__(self, name, email):
        self.name = name
        self.email = email


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

        else:
            usr = users(user, "")
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
    if "user" in session:
        user = session["user"]

        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            found_user = users.query.filter_by(name=user).first()
            found_user.email = email
            db.session.commit()
            flash ("Email saved!", "info")
        else:
            if "email" in session:
                email = session["email"]
        return render_template("user.html", email=email)
    else:
        return redirect(url_for("login"))


@app.route("/logout/")
def logout():
    if "user" in session:
        flash("Logged out successfully!", "info")
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("login"))


with app.app_context():
    app.run(debug=True)
    print("cu verde")
    db.create_all()
