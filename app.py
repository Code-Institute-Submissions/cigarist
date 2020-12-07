import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_cigars")
def get_cigars():
    tastingNotes = mongo.db.tastingNotes.find()
    return render_template("cigar_posts.html", tastingNotes=tastingNotes)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("You are registered")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Hello, {}".format(
                        request.form.get("username")))
                    return redirect(url_for(
                        "profile", username=session["user"]))
            else:
                flash("Your Username and/or Passward is incorrect.")
                return redirect(url_for("login"))

        else:
            flash("Your Username and/or Passward is incorrect.")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_post", methods=["GET", "POST"])
def add_post():
    if request.method == "POST":
        tastingNotes = {
            "cigarImage": request.form.get("cigarImage"),
            "cigarBrand": request.form.get("cigarBrand"),
            "vitola": request.form.get("vitola"),
            "ringGauge": request.form.get("ringGauge"),
            "handMade": request.form.get("handMade"),
            "cigarStrength": request.form.get("cigarStrength"),
            "cigarDraw": request.form.get("cigarDraw"),
            "cigarFlavour": request.form.get("cigarFlavour"),
            "cigarAroma": request.form.get("cigarAroma"),
            "cigarBurn": request.form.get("cigarBurn"),
            "price": request.form.get("price"),
            "notes": request.form.get("notes"),
            "created_by": session["user"]
        }
        mongo.db.tastingNotes.insert_one(tastingNotes)
        flash("You Have Made A Post!")
        return redirect(url_for("add_post"))

    return render_template("add_post.html")


@app.route("/edit_post/<post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    if request.method == "POST":
        submit = {
            "cigarImage": request.form.get("cigarImage"),
            "cigarBrand": request.form.get("cigarBrand"),
            "vitola": request.form.get("vitola"),
            "ringGauge": request.form.get("ringGauge"),
            "handMade": request.form.get("handMade"),
            "cigarStrength": request.form.get("cigarStrength"),
            "cigarDraw": request.form.get("cigarDraw"),
            "cigarFlavour": request.form.get("cigarFlavour"),
            "cigarAroma": request.form.get("cigarAroma"),
            "cigarBurn": request.form.get("cigarBurn"),
            "price": request.form.get("price"),
            "notes": request.form.get("notes"),
            "created_by": session["user"]
        }
        mongo.db.tastingNotes.update({"_id": ObjectId(post_id)}, submit)
        flash("Your Post is Updated!")

    tastingNotes = mongo.db.tastingNotes.find_one({"_id": ObjectId(post_id)})
    return render_template("edit_post.html", tastingNotes=tastingNotes)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True) 

# Turn to false before project submission
