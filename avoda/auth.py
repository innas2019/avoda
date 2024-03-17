from flask import Blueprint
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
    session,
)
from werkzeug.security import check_password_hash, generate_password_hash
from avoda.db import get_db
import datetime


def get_roles(user_id):
    # "select u.name, u.password, u.isactive, r.name as role from user as u left join role as r, user_role on user_role.user_id=u.id and user_role.role_id=r.id
    query = "select name from role, user_role where user_role.user_id=? and user_role.role_id=role.id"
    roles = get_db().execute(query, (user_id,)).fetchall()
    session["roles"] = []
    for r in roles:
        session["roles"].append(r["name"])


def update_settings(s):
    db = get_db()
    try:
        db.execute(
            "update user set settings=? where id=?",
            (s, session.get("user_id                ")),
        )
        db.commit()
    except db.Error as e:
        flash(e)


bp = Blueprint("auth", __name__)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )
        get_roles(g.user["id"])


@bp.route("/")
@bp.route("/title")
def title():
    return render_template("title.html", title="'פּרוֹיֶקט 'עבודה ")


@bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form["name"]
        password = request.form["password"]
        password2 = request.form["password2"]
        error = None
        if password != password2:
            error = "ошибка при вводе пароля"
        if error is None:
            db = get_db()

            try:
                db.execute(
                    "INSERT INTO user (name, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)
    else:
        return render_template("auth/register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        username = request.form["name"]
        password = request.form["password"]
        db = get_db()

        error = None
        user = db.execute("SELECT * FROM user WHERE name = ?", (username,)).fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            get_roles(user["id"])
            session["user_id"] = user["id"]
            session["name"] = username
            if user["settings"] == None:
                session["filter"] = ""
            else:
                session["filter"] = user["settings"]
            return redirect(url_for("posts.list"))

        flash(error)
        return render_template("auth/login.html", title="Вход")

    else:
        return render_template("auth/login.html", title="Вход")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.title"))
