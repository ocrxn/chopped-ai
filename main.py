import os
from flask import Flask, render_template, abort, send_file,redirect, url_for, session, request, flash, jsonify, send_from_directory
from dotenv import load_dotenv
from db_conn import Connection
from email_verif import connect_smtp
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER, CMPR_UPLOAD_FOLDER, OUTPUT_FOLDER
import signal
import json
import subprocess
from file_handling import FileHandler
import time



app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('app_key')

#Upload file parameters
app.config['MAX_CONTENT_LENGTH'] = 1024*1024 * 1024 * 50 #50 GB


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
            file = request.files.get('upload_file')
            if not file or file.filename == "":
                return jsonify({'Error': 'File part not found.'})

            # Parse filename
            filename = secure_filename(file.filename)
            upload_path = os.path.join(UPLOAD_FOLDER, filename)

            chunk_size = 1024 * 1024
            with open(upload_path, "wb") as f:
                while True:
                    chunk = file.stream.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)

            kwargs = {
                "filename": filename,
                "input_path": upload_path,
                "hardware_encode": request.form.get("hardware_encode"),
                "output_format": request.form.get("output_format") or "mp4",
                "output_dir": CMPR_UPLOAD_FOLDER
            }

            fh = FileHandler()
            result = fh.compress_video(kwargs)

            # Compressed file name (matches compress_video output)
            name, _ = os.path.splitext(filename)
            compressed_filename = f"cmpr_{name}.{kwargs['output_format']}"

            return redirect(url_for("display", filename=compressed_filename))

        except FileNotFoundError:
            return jsonify({'Error': 'No file uploaded.'})
        except Exception as e:
            return jsonify({"An exception has occurred": f'{e}'})


@app.route("/display/<filename>")
def display(filename):
    is_logged_out = require_login()
    if is_logged_out:
        return is_logged_out

    return render_template("display.html", filename=filename)


@app.route("/cmpr_uploads/<filename>")
def cmpr_uploads(filename):
    path = os.path.join(CMPR_UPLOAD_FOLDER, filename)
    if not os.path.exists(path):
        return "File not found", 404

    return send_file(path, as_attachment=False)

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
        session.pop("user", None)

        #Set user status not active in DB
        cn = Connection()
        cn.update_status("UPDATE public.users SET is_active=FALSE WHERE username=%s",username)

        return redirect(url_for("login"))
    else:
        flash("Internal server error: unable to locate session/user.")


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/delete", methods=["POST"])
def delete():
    is_logged_out = require_login()
    if is_logged_out:
        return is_logged_out
    
    if request.method == "POST":
        del_username = request.form["del-username"]
        del_password = request.form["del-password"]

        if del_username != session.get("user"):
            flash("Username does not match current user.")
            return redirect(url_for("profile"))

        cn = Connection()
        if cn.confirm_user(del_username, del_password):
            delete = cn.delete_user(del_username)
            if delete:
                flash("Account successfully deleted")
                return redirect(url_for("login"))
            else:
                return jsonify({"Database Error":"Account failed to delete. Please try again."})
        flash("Incorrect password")
        return redirect(url_for("profile"))
    
    return jsonify({"Error Occurred":"Method /delete has failed"})


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
    app.run(host="0.0.0.0", port=5050, debug=False)