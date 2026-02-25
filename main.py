import os
from flask import Flask, render_template, abort, redirect, url_for, session, request, flash, jsonify, send_from_directory
from dotenv import load_dotenv
from db_conn import Connection
from email_verif import connect_smtp
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER, OUTPUT_FOLDER
import signal
import json
import subprocess
from file_handling import FileHandler



app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('app_key')

#Upload file parameters
app.config['MAX_CONTENT_LENGTH'] = 1024*1024 * 1 #1 MB


@app.errorhandler(413)
def max_file_size_exceeded(e):
    return "File size exceeded!", 413

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

@app.route("/profile", methods=["GET","POST"])
def profile():
    is_logged_out = require_login()
    if is_logged_out:
        return is_logged_out
    return render_template("profile.html")

@app.route("/upload", methods=["GET","POST"])
def upload():
    is_logged_out = require_login()
    if is_logged_out:
        return is_logged_out
    
    if request.method == "GET":
        return render_template("upload.html")

    if request.method == "POST":
        try:
            #Return Error if upload_file not found
            file = request.files.get('upload_file')
            if not file or file.filename == "":
                return jsonify({'Error':'File part not found.'})
            

            #Parse filename and arguments
            filename = secure_filename(file.filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            os.makedirs(OUTPUT_FOLDER, exist_ok=True)
            path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(path)

            #Store values in dictionary
            kwargs = {
                "filename": filename,
                "path": path,
                "video_format": request.form.get("video_format"),
                "audio_format": request.form.get("audio_format"),
                "output_format": request.form.get("output_format")
            }
                       
            #File Handler (file_handling.py)
            fh = FileHandler()
            compress_video = fh.compress_video(kwargs)
            print(compress_video)

            return redirect(url_for("display", filename=filename))

        except FileNotFoundError:
            return jsonify({'Error':'No file uploaded.'})
        except Exception as e:
            return jsonify({"An exception has occurred":f'{e}'})



#Return display.html
@app.route("/display/<filename>")
def display(filename):
    is_logged_out = require_login()
    if is_logged_out:
        return is_logged_out
    
    return render_template("display.html",filename=filename)

#Return uploaded video
#Implemented in <display.html>
@app.route("/chopped_uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

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

        #!!!!Temporarily disabled to prevent backend complications  #TODO
            #Send 2FA code to user email for verification
            #See email_verify.py for implementation
            # connect_smtp(username, email)
            
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

@app.route("/delete", methods=["POST"])
def delete():
    is_logged_out = require_login()
    if is_logged_out:
        return is_logged_out
    return jsonify({"Account deleted":"success","Message":"Your account has been successfully deleted and all data has been erased."})

@app.route("/shutdown", methods=["POST"])
def shutdown():
    if session.get("user") != 'admin':
        abort(403)
    shutdown_server = request.environ.get('werkzeug.server.shutdown')
    if shutdown_server is None:
        print(f"Flask server not using werkzeug. Shutting down using SIGINT...")
        os.kill(os.getpid(), signal.SIGINT)
        return jsonify({"SIGINT trigger":"Success","Content":"Flask server shutting down..."})
    else:
        shutdown_server()
        return jsonify({"Werkzeug trigger":"Success","Content":"Flask server shutting down..."})


if __name__ == "__main__":
    app.run()

