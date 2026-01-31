import os
from flask import Flask, render_template, redirect, url_for, session, request, flash
from dotenv import load_dotenv
from db_conn import Connection
from email_verif import connect_smtp
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('app_key')


def require_login():
    if "user" not in session:
        return redirect(url_for("login"))
    return None

@app.route("/", methods=["GET","POST"])
def home():
    is_logged_out = require_login()
    if is_logged_out:
        return is_logged_out
    return render_template("home.html")

@app.route("/upload", methods=["GET","POST"])
def upload():
    is_logged_out = require_login()
    if is_logged_out:
        return is_logged_out
    
    if request.method == "GET":
        return render_template("upload.html")

    if request.method == "POST":
        file = request.files["upload_file"]
        filename = secure_filename(file.filename)
        print(f"Video uploaded: {filename}")

        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)
        return redirect(url_for("home"))


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
            #Store user in session
            session["user"] = username

            #Set user status active in DB
            cn.update_status("UPDATE public.users SET is_active=TRUE WHERE username=%s",username)
            
            return redirect(url_for("home"))
        
        flash("Invalid username or password. Please try again.")
        return redirect(url_for("login"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        print(f"{username}\n{email}\n{password}")

        cn = Connection()

        #Check if user already exists
        if cn.confirm_user(username, password):
            flash("User already exists. Try logging in.")
            return redirect(url_for("login"))
        
        #Create new user in DB if not exists
        if cn.create_user(username, email, password):
            #Store user in session
            session["user"] = username

            #Set user status active in DB
            cn.update_status("UPDATE public.users SET is_active=TRUE WHERE username=%s",username)

            # #Send 2FA code to user email for verification
            connect_smtp(username, email)
            
            return redirect(url_for("home"))


@app.route("/logout")
def logout():
    username = session.get("user")
    if username:
        #Remove user from session
        session.pop("user", None)

        #Set user status not active in DB
        cn = Connection()
        cn.update_status("UPDATE public.users SET is_active=FALSE WHERE username=%s",username)

        return redirect(url_for("login"))
    else:
        flash("Internal server error: unable to locate session/user.")


@app.route("/about")
def about():
    is_logged_out = require_login()
    if is_logged_out:
        return is_logged_out
    return render_template("about.html")


if __name__ == "__main__":
    app.run()

