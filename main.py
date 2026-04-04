from flask import Flask, render_template, abort, send_file,redirect, url_for, session, request, flash, jsonify, send_from_directory
from dotenv import load_dotenv
from email_verif import connect_smtp
from werkzeug.utils import secure_filename
import os
import signal
import json
import subprocess
import time
import datetime
import tempfile
import shutil

from db_conn import Connection
from config import UPLOAD_FOLDER, CLIPS_FOLDER, ZIP_FOLDER
from file_handling import FileHandler

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('app_key')

#Upload file parameters
app.config['MAX_CONTENT_LENGTH'] = 1024*1024 * 1024 * 15 #15 GB

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
        file_size = app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024)
        base = 'MB' if file_size < 1024 else 'GB'
        if base == 'GB':
            file_size /= 1024
        return render_template("upload.html", file_size=file_size, base=base)

    if request.method == "POST":
        try:
            #Get video/audio files from website and return if empty
            video_file = request.files.get('video_upload_file')
            audio_file = request.files.get('audio_upload_file')
            if not video_file or video_file.filename == "":
                return jsonify({'Error': 'File part not found.'})

            #Create secure filenames, extract exts, and make paths
            video_filename = secure_filename(video_file.filename)
            video_extension = os.path.splitext(video_filename)[1].lower().replace(".", "")
            video_upload_path = os.path.join(UPLOAD_FOLDER, video_filename)

            audio_filename = secure_filename(audio_file.filename) if audio_file else None
            audio_extension = os.path.splitext(audio_filename)[1].lower().replace(".", "") if audio_file else None
            audio_upload_path = os.path.join(UPLOAD_FOLDER, audio_filename) if audio_file else None

            #Get the type of compression encoding user selected
            encoding = request.form.get("hardware_encode")

            #Create a temporary file where video gets written
            with tempfile.NamedTemporaryFile(suffix=f".{video_extension}", delete=False) as temp_vid:
                temp_vid_path = temp_vid.name
                video_file.save(temp_vid_path)
                temp_vid.flush()
            
            temp_audio_path = None
            if audio_file:
                with tempfile.NamedTemporaryFile(suffix=f".{audio_extension}", delete=False) as temp_audio:
                    temp_audio_path = temp_audio.name
                    audio_file.save(temp_audio_path)
                    temp_audio.flush()
      
            try:
                fh = FileHandler()
                kwargs = {
                        "vid_filename": video_filename,
                        "audio_filename": audio_filename,
                        "video_path": temp_vid_path,
                        "audio_path": temp_audio_path,
                        "encoding": encoding,
                        "vid_ext": video_extension,
                        "audio_ext": audio_extension,
                        "output_dir": UPLOAD_FOLDER
                    }
                
                #Copy audio file
                if audio_file:
                    shutil.move(temp_audio_path,audio_upload_path)
                
                result = {"status": "skipped", "cmpr_size": os.path.getsize(temp_vid_path)}
                #Copy video file
                if encoding and encoding != "none":
                    # Compress the video if user selected a compression mode
                    result = fh.compress_video(kwargs)
                    print(result)

                else:
                    # Skip compression and move video from temp to uploads
                    shutil.move(temp_vid_path,video_upload_path) 
                
                cmpr_size = result.get("cmpr_size")

                #Zip the files
                # fh.zip_clips(filename=video_filename,clips_dir=CLIPS_FOLDER,zip_dir=ZIP_FOLDER)


            except Exception as e:
                flash(f"An error has occurred: {e}")
                return redirect(url_for('upload'))
            finally:
                if temp_vid_path and os.path.exists(temp_vid_path):
                    os.remove(temp_vid_path)
                if temp_audio_path and os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
            return redirect(url_for("display", filename=video_filename, cmpr_mode=encoding, cmpr_size=cmpr_size))

        except FileNotFoundError:
            flash("Error: No file uploaded")
            return redirect(url_for('upload'))
        
        except Exception as e:
            flash(f"Exception has occurred: {e}")
            return redirect(url_for('upload'))

@app.route("/display/<filename>")
def display(filename):
    is_logged_out = require_login()
    if is_logged_out:
        return is_logged_out
    cmpr_mode = request.args.get("cmpr_mode")
    cmpr_size_long = int(request.args.get("cmpr_size")) / (1024 * 1024)
    cmpr_size = "{:.2f}".format(cmpr_size_long)

    return render_template("display.html", filename=filename, cmpr_mode=cmpr_mode, cmpr_size=cmpr_size)


@app.route("/get_video/<filename>")
def get_video(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
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
    try:
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
                    flash("Database failed to query action. Please try again.")
                    return redirect(url_for("profile"))
            flash("Incorrect password")
            return redirect(url_for("profile"))
    except Exception as e:
        flash(f"An unknown error has occurred: {e}")
        return redirect(url_for("profile"))

@app.route("/explain")
def explain():
    return render_template("explain.html")

@app.route("/shutdown", methods=["POST"])
def shutdown():
    if session.get("user") != 'admin':
        abort(403)
    shutdown_server = request.environ.get('werkzeug.server.shutdown')
    if shutdown_server is None:
        print(f"Flask server not using werkzeug. Shutting down using SIGINT...")
        os.kill(os.getpid(), signal.SIGINT)
        return redirect("https://www.google.com")
    else:  
        shutdown_server()
        return redirect("https://www.google.com")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=False)