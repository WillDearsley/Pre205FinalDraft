import os
import json
from flask import render_template, request, make_response, Blueprint, url_for, flash, redirect
from werkzeug.security import generate_password_hash, check_password_hash

from flask_app import db # -------------------> THIS IS THE DATABASE ABJECT <------------------------------------
from flask_app.models import Users

api = Blueprint("api", __name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
with open(f"{APP_ROOT}/resources/sample.json") as f:
    tickers = json.load(f)

# endpoint for signing up users
@api.route("/signupendpoint", methods=["POST"])
def signupendpoint():
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm-password")

    if not email or not password or not confirm_password:
        return "<div class='alert error'>All fields are required!</div>"

    if password != confirm_password:
        return "<div class='alert error'>Passwords do not match!</div>"

    if Users.query.filter_by(email=email).first():
        return "<div class='alert error'>Email already exists!</div>"

    hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
    new_user = Users(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return "<div class='alert success'>Account created successfully!</div>"


@api.route("/loginendpoint", methods=["POST"])
def loginendpoint():
    email = request.form.get("email")
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False

    if not email or not password:
        return "<div class='alert error'>Please provide both email and password</div>"

    user = Users.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return "<div class='alert error'>Invalid email or password</div>"

    # Log the user in using Flask-Login
    # login_user(user, remember=remember)

    # Return success message with redirect
    return """
    <div class='alert success'>Login successful! Redirecting...</div>
    <script>
        setTimeout(function() {
            window.location.href = '/dashboard';
        }, 1000);
    </script>
    """


@api.route("/api/v1/search", methods=["POST"])
def search():
    search_term = request.form.get("search")

    if not len(search_term):
        return render_template("test_table.html", tickers=[])

    res_tickers = []
    for ticker in tickers["data"]:
        if search_term.lower() in ticker["name"].lower():
            res_tickers.append(ticker)

    return render_template("test_table.html", tickers=res_tickers)

# visit https://localhost:5000/users to see the users you added in terminal
@api.route("/users", methods=["GET"])
def get_users():
    # Fetch all users from the database
    users = Users.query.all()
    return {"users": [user.email for user in users]}