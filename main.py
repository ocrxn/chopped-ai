import os
from flask import Flask, render_template, redirect, url_for, session, request, flash
from dotenv import load_dotenv

from db_conn import Connection

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('app_key')


def require_login():
    if "user" not in session:
        return redirect(url_for("login"))
    return None

@app.route("/")
def home():
    is_logged_out = require_login()
    if is_logged_out:
        return is_logged_out
    return render_template("home.html")
 

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        #Call to db_conn.py to validate credentials
        cn = Connection()
        if cn.confirm_user(username, password):
            session["user"] = username   # store in session
            return redirect(url_for("home"))
        
        flash("Invalid username or password. Please try again.")
        return redirect(url_for("login"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        #Call to db_conn.py to create new user
        cn = Connection()
        if cn.confirm_user(username, password):
            flash("User already exists. Try logging in.")
            return redirect(url_for("login"))
            
        if cn.create_user(username, password):
            session["user"] = username   # store in session
            return redirect(url_for("home"))


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/about")
def about():
    is_logged_out = require_login()
    if is_logged_out:
        return is_logged_out
    return render_template("about.html")


if __name__ == "__main__":
    app.run()

