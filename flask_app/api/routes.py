import os
import json
from flask import render_template, request,make_response, Blueprint, url_for

from flask_app import db # -------------------> THIS IS THE DATABASE ABJECT <------------------------------------
from flask_app.models import Users

api = Blueprint("api", __name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
with open(f"{APP_ROOT}/resources/sample.json") as f:
    tickers = json.load(f)

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

# Testing db to add data to automatically created users table
# make a curl request to: curl -X POST -d "username=testuser&email=test@example.com" http://localhost:5000/add_user on your terminal
@api.route("/add_user", methods=["POST"])
def add_user():
    username = request.form.get("username")
    email = request.form.get("email")

    # Create a new user
    new_user = Users(username=username, email=email)
    db.session.add(new_user)
    db.session.commit()

    return f"User {username} added!"

# visit https://localhost:5000/users to see the users you added in terminal
@api.route("/users", methods=["GET"])
def get_users():
    # Fetch all users from the database
    users = Users.query.all()
    return {"users": [user.username for user in users]}