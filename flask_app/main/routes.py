import os
from flask import render_template, request, make_response, Blueprint, url_for, send_from_directory, current_app
from flask_app import db # -------------------> THIS IS THE DATABASE ABJECT <------------------------------------

main = Blueprint("main", __name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@main.route("/", methods=["GET", "POST"])
@main.route("/index", methods=["GET", "POST"])
def index():

    meta = {
        "title": "Home - Speckle Invoice",
        "description": "Join Speckle Invoice today to simplify invoice generation for your bussiness",
        "og_url": url_for('main.index', _external=True)
    }

    return render_template("index.html", meta=meta)

@main.route("/signup", methods=["GET", "POST"])
def signup():

    meta = {
        "title": "Sign Up - Speckle Invoice",
        "description": "Create an account on Speck Invoice today. It's Free!",
        "og_url": url_for('main.signup', _external=True)
    }

    return render_template("signup.html", meta=meta)

@main.route("/signin", methods=["GET", "POST"])
def signin():

    meta = {
        "title": "Sign In - Speckle Invoice",
        "description": "Sign in to Speck Invoice today",
        "og_url": url_for('main.signin', _external=True)
    }

    return render_template("signin.html", meta=meta)


@main.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    meta = {
        "title": "Dashboard - Speckle Invoice",
        "description": "Sign in to Speck Invoice today",
        "og_url": url_for('main.dashboard', _external=True)
    }

    return render_template("dashboard.html", meta=meta)

@main.route("/forgot", methods=["GET", "POST"])
def forgot():

    meta = {
        "title": "Forgot Password - Speckle Invoice",
        "description": "If your having issues remembering your password",
        "og_url": url_for('main.index', _external=True)
    }

    return render_template("forgot.html", meta=meta)



@main.route("/sitemap.xml")
def sitemap():
    pages = [
      {"loc": url_for("main.index", _external=True)},
      #{"loc": url_for("main.search", _external=True)},
    ]
  
    sitemap_xml = render_template("sitemap_template.xml", pages=pages)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"
  
    return response

@main.route("/robots.txt")
def static_from_root():
    return send_from_directory(current_app.static_folder, request.path[1:])