from flask import Flask, render_template, abort, send_file, redirect, url_for, session, request, flash, jsonify, send_from_directory
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from waitress import serve
import os
import signal
import json
import subprocess
import time
import datetime
import tempfile
import shutil
import logging

logging.basicConfig(filename="app.log",
                    level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s")

from db_conn import Connection
from config import UPLOAD_FOLDER, CLIPS_FOLDER, ZIP_FOLDER, APP_KEY
from file_handling import compress_video, zip_clips
from json_maker import create_json_file
from processor import run_processor

app = Flask(__name__)
load_dotenv()
app.secret_key = APP_KEY

app.config['MAX_CONTENT_LENGTH'] = 1024*1024 * 1024 * 15

@app.errorhandler(413)
def max_file_size_exceeded():
    """
    Returns Error 413 if user uploads file exceeding size 
    specified in app.config['MAX_CONTENT_LENGTH]
    """
    flash("Error 413: File size exceeded!")
    return redirect(url_for("upload"))

def require_login():
    """
    Checks if user is in session, otherwise returns user to login screen
    """
    if "user" not in session:
        return redirect(url_for("login"))
    return None

@app.route("/", methods=["GET","POST"])
def home():
    """
    Return main page [requires logged in]
    """
    is_logged_out = require_login()
    if is_logged_out:
        return is_logged_out
    return render_template("home.html")

@app.route("/upload", methods=["GET","POST"])
def upload():
    """
    GET: Return upload page [requires logged in]\n
    POST: Uploads the video to backend and calls various other functions
    to create the zip file using the video
    """
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
                logging.error("[upload] Error 404: File could not be found.")
                flash("[upload] Error 404: File could not be found.")
                return redirect(url_for("upload"))

            #Create secure filenames, extract exts, and make paths
            video_filename = secure_filename(video_file.filename)
            video_name_only = os.path.splitext(video_filename)[0].lower().replace(".", "")
            video_extension = os.path.splitext(video_filename)[1].lower().replace(".", "")
            video_upload_path = os.path.join(UPLOAD_FOLDER, video_filename)

            audio_filename = secure_filename(audio_file.filename) if audio_file else None
            audio_name_only = os.path.splitext(audio_filename)[0].lower().replace(".", "") if audio_file else None
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
                    result = compress_video(kwargs)
                    
                else:
                    # Skip compression and move video from temp to uploads
                    shutil.move(temp_vid_path,video_upload_path) 

                #<---------Make json file--------------->
                create_json_file(video_upload_path,audio_upload_path,video_name_only)

                #<---------Create clips--------------->
                run_processor()
                
                #<---------Zip clips--------------->
                zip_clips(filename=video_name_only,clips_dir=CLIPS_FOLDER,zip_dir=ZIP_FOLDER)
                cmpr_size = result.get("cmpr_size")

                #<---------Delete original video if encoding=None--------------->
                enable_video = True
                if not encoding or encoding == "none":
                    enable_video = False
                    os.remove(video_upload_path)
                    logging.info(f"[upload] (encoding=None) Removed original video file: {video_name_only} ")

            except Exception as e:
                logging.error(f"[upload] An error has occurred: {e}")
                flash(f"An error has occurred: {e}")
                return redirect(url_for('upload'))
            finally:
                if temp_vid_path and os.path.exists(temp_vid_path):
                    os.remove(temp_vid_path)
                if temp_audio_path and os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
            return redirect(url_for("display",
                                    enable_video = enable_video,
                                    filename=video_filename, 
                                    zip_name = f"{video_name_only}.zip", 
                                    cmpr_mode=encoding, cmpr_size=cmpr_size))

        except FileNotFoundError:
            logging.error("[upload] Error: No file uploaded")
            flash("Error: No file uploaded")
            return redirect(url_for('upload'))
        
        except Exception as e:
            logging.error(f"[upload] Exception has occurred: {e}")
            flash(f"Exception has occurred: {e}")
            return redirect(url_for('upload'))

@app.route("/display/<filename>")
def display(filename):
    """
    Return display page of video/zip file [requires logged in]
    """
    is_logged_out = require_login()
    if is_logged_out:
        return is_logged_out
    enable_video = request.args.get("enable_video")
    zip_name = request.args.get("zip_name")
    cmpr_mode = request.args.get("cmpr_mode")
    cmpr_size_long = int(request.args.get("cmpr_size")) / (1024 * 1024)
    cmpr_size = "{:.2f}".format(cmpr_size_long)

    return render_template("display.html", enable_video=enable_video,filename=filename, zip_name=zip_name, cmpr_mode=cmpr_mode, cmpr_size=cmpr_size)


@app.route("/get_video/<filename>")
def get_video(filename):
    """
    Returns the video file for display.html
    """
    path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(path):
        logging.error("[get_video] Error 404: File not found.")
        flash("Error 404: File not found.")
        return redirect(url_for("home"))

    return send_file(path, as_attachment=True)

@app.route("/download_zip/<filename>")
def download_zip(filename):
    """
    Returns the zip file path for display.html as downloadable attachment
    """
    path = os.path.join(ZIP_FOLDER, filename)
    
    if not os.path.exists(path):
        logging.error("[download_zip] Error 404: Zip file not found.")
        flash("Error 404: Zip file not found.")
        return redirect(url_for("home"))

    return send_file(path, as_attachment=True)

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    GET: Returns login page\n
    POST: Validates input credentials against PostgreSQL database
    """
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
        
        logging.warning("[login] Invalid username or password. Please try again.")
        flash("Invalid username or password. Please try again.")
        return redirect(url_for("login"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    """
    GET: Returns signup page\n
    POST: Create a user account in PostgreSQL database
    """
    if request.method == "GET":
        return render_template("signup.html")
    
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        cn = Connection()

        #Check if user already exists
        if cn.confirm_user(username, password):
            logging.warning("[signup] User already exists. Try logging in.")
            flash("User already exists. Try logging in.")
            return redirect(url_for("login"))
        
        #Create new user in DB if not exists
        if cn.create_user(username, email, password):
            session["user"] = username

            #Set user status active in DB
            cn.update_status("UPDATE public.users SET is_active=TRUE WHERE username=%s",username)

            return redirect(url_for("home"))


@app.route("/logout")
def logout():
    """
    Pops user from session and returns login screen
    """
    username = session.get("user")
    if username:
        session.pop("user", None)

        #Set user status not active in DB
        cn = Connection()
        cn.update_status("UPDATE public.users SET is_active=FALSE WHERE username=%s",username)

        return redirect(url_for("login"))
    else:
        logging.error("[logout] Internal server error: unable to locate session/user.")
        flash("Internal server error: unable to locate session/user.")


@app.route("/profile", methods=["GET","POST"])
def profile():
    """
    Returns profile page [requires logged in]
    """
    is_logged_out = require_login()
    if is_logged_out:
        return is_logged_out
    return render_template("profile.html")


@app.route("/delete", methods=["POST"])
def delete():
    """
    POST: Delete account from database [requires logged in]
    """
    try:
        is_logged_out = require_login()
        if is_logged_out:
            return is_logged_out
        
        if request.method == "POST":
            del_username = request.form["del-username"]
            del_password = request.form["del-password"]

            if del_username != session.get("user"):
                logging.warning("[delete] Username does not match current user.")
                flash("Username does not match current user.")
                return redirect(url_for("profile"))

            cn = Connection()
            if cn.confirm_user(del_username, del_password):
                delete = cn.delete_user(del_username)
                if delete:
                    logging.info("[delete] Account successfully deleted.")
                    flash("Account successfully deleted")
                    return redirect(url_for("login"))
                else:
                    logging.error("[delete] Database failed to query action. Please try again.")
                    flash("Database failed to query action. Please try again.")
                    return redirect(url_for("profile"))
            logging.warning("[delete] Incorrect password")
            flash("Incorrect password")
            return redirect(url_for("profile"))
    except Exception as e:
        logging.error(f"[delete] An unknown error has occurred: {e}")
        flash(f"An unknown error has occurred: {e}")
        return redirect(url_for("profile"))


@app.route("/about")
def about():
    """
    Return about page
    """
    return render_template("about.html")


@app.route("/explain")
def explain():
    """
    Return explain page
    """
    return render_template("explain.html")


@app.route("/shutdown", methods=["POST"])
def shutdown():
    """
    POST: Shutdown the Flask server using werkzeug or SIGINT [requires logged in as admin]
    """
    if session.get("user") != 'admin':
        abort(403)
    shutdown_server = request.environ.get('werkzeug.server.shutdown')
    if shutdown_server is None:
        os.kill(os.getpid(), signal.SIGINT)
        logging.warning("[shutdown] Flask server has shutdown using signal.SIGINT")
        return redirect("https://www.google.com")
    else:  
        shutdown_server()
        logging.warning("[shutdown] Flask server has shutdown werkzeug.server.shutdown")
        return redirect("https://www.google.com")

if __name__ == "__main__":
    serve(app, port=5050, max_request_body_size=1024*1024*1024 * 15)