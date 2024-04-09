import urllib.parse

from flask import Flask, render_template, flash, redirect, request, session, jsonify, Response
import os
from typing import Dict, List
import secrets
import string

from Page import Page
from db import database
from User import User
from security import *

app = Flask(__name__)


@app.route("/auth", methods=['POST'])
def auth() -> Response:
    auth_type: str = request.form['auth-type'].lower()
    if auth_type == "login":
        return login()
    elif auth_type == "register":
        return register()
    return redirect("/" + request.form['auth-type'])


@app.route("/")
def default() -> str:
    return render_template("shortener.html")


@app.route('/s/<short>')
def get_shorten(short: str) -> Response:
    page = database.select_one("links", {"short": short}, ['id', 'user_id', 'url', 'visits'])
    if page is not None:
        if 'user' not in session or page['user_id'] != session['user']['id']:
            database.update("links", page['id'], {"visits": int(page['visits'])+1})
        return redirect(page['url'])

    return redirect('/')


@app.route("/login", methods=['POST'])
def login() -> Response:
    username = request.form['username']
    password = request.form['password']
    user = database.select_one("users", {"username": username})
    if user is None or not verify_password(user['password'], password):
        flash("Wrong username or password!", "login_error")
    else:
        session['user']: User = User(user['id'], user['username'], user['password']).to_json()
    return redirect('/')


@app.route("/logout")
def logout() -> Response:
    if 'user' in session:
        del session['user']
    return redirect('/')


@app.route('/profile')
def profile() -> Response | str:
    if 'user' not in session:
        return redirect('/')

    pages: List[Page] = []
    database_pages = database.select_many("links",  {"user_id": session['user']['id']})
    for page in database_pages:
        pages.append(Page(page['id'], page['user_id'], page['url'], page['short'], page['visits']))
    return render_template("profile.html", pages=pages, base_url=urllib.parse.urlparse(request.host_url).hostname)


@app.route("/register", methods=['POST'])
def register() -> Response:
    username = request.form['username']
    password = hash_password(request.form['password'])
    already_exists: bool = not database.select_one("users", {"username": username}) is None
    if not already_exists:
        database.insert("users", {"username": username, "password": password})
        return login()

    flash("Account with this username already exists.", "login_error")
    return redirect('/')


@app.route("/shorten", methods=['POST'])
def shorten() -> Response:
    link: str = request.form['link']
    user: int = session['user']['id'] if 'user' in session else None
    values: Dict[str, str | int] = {"user_id": user, "url": link}
    while True:
        short: str = generate_short_link()
        values['short'] = short
        res = database.insert("links", values)
        if res != database.DatabaseResponse.NOT_UNIQUE:
            break
    return jsonify({'shorten': values['short']})


def generate_short_link(length=16) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True)
