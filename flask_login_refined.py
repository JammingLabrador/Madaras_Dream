# GOAL: make user auth that leads to a form page, then t.b.d

from flask import Flask, request, render_template, url_for, redirect, session, render_template_string
from flask_login import LoginManager, login_required, login_user, logout_user, current_user, UserMixin
import sqlite3
import os
from dotenv import load_dotenv
import requests
import operator
from Auth_Training import signup, login
import json

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth_land"

load_dotenv("shush.env")
secret_key = os.getenv("secret_key")
app.config["SECRET_KEY"] = secret_key

class User(UserMixin):
    def __init__(self, user_id):
        self.user_id = user_id
    def get_id(self): # this overrides the UserMixin's method itself, which expects the name "id"
                      # but I use "user_id" instead
        return self.user_id
# This User class is a child of UserMixin, it is a holder for the data about the user, which allows you to
# pass the data into your database for persistence
# it is used because it organises user data into attributes, and is used to identify the user so that
# flask-login's boilerplate can know who it is and tell the login_required decorator to let him through

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)
# pure boilerplate

@app.route("/", methods=["GET", "POST"])
@login_required # LIFESAVER: don't gotta do no session user_id checking shit
def home():
    if request.method == "POST":
        user_name = request.form.get("username")
        user_country = request.form.get("country")
        user_dob = request.form.get("dob")
        user_sex = request.form.get("sex")
        session["user_info"] = [user_name, user_country, user_dob, user_sex]
        return redirect(url_for("user_profile"))

    url = "https://restcountries.com/v3.1/all?fields=name"
    response = requests.get(url).json()
    country_names = []
    for country in response:
        parsed_name = country["name"]["official"]
        country_names.append(parsed_name)

    return render_template("form_home.html", country_names=country_names)


@app.route("/auth_land", methods=["GET", "POST"])
def auth_land():
    if request.method == "POST":
        signup_e = request.form.get("signup_email")
        signup_p = request.form.get("signup_password")
        login_e = request.form.get("login_email")
        login_p = request.form.get("login_password")

        is_signed_up = signup(signup_e, signup_p)
        is_logged_in = login(login_e, login_p)

        if operator.xor(bool(is_signed_up), bool(is_logged_in)):
            conn = sqlite3.connect("email_password_repo.db")
            cursor = conn.cursor()

            if is_signed_up:
                params = (signup_e, signup_p)
            else:
                params = (login_e, login_p)

            cursor.execute("select given_id from email_password where email = ? and password = ?",
                           params)
            raw_id = cursor.fetchone()
            given_id = raw_id[0]
            netizen = User(given_id)
            login_user(netizen)
            conn.close()
            return redirect(url_for("home"))
        else:
            return render_template("user_auth.html", error="damn, somebody fucked up")
    return render_template("user_auth.html")

@app.route("/user_profile")
@login_required
def user_profile():
    if any(x is None or x == "" for x in session.get("user_info")):
        return redirect(url_for("home"))
    else:
        url = "https://api.waifu.im/images?included_tags=shounen"
        response = requests.get(url).json()["items"][0]["url"]

        return render_template("user_profile.html", image_url=response)

if __name__ == "__main__":
    app.run(debug=True)