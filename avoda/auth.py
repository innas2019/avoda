from flask import Blueprint
from flask import ( Blueprint, flash, redirect, render_template, request, url_for,  session)
from flask_login import current_user, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from avoda import db
from avoda.models import Users

def get_roles(user):
    session["roles"] = []
    for r in user.roles:
        session["roles"].append(r.name)
        

def update_settings(s):
    id=session["_user_id"] #user-login set parameter 
    user=db.session.get(Users, int(id)) 
    user.settings = s
    db.session.commit()
    

bp = Blueprint("auth", __name__)
user = None


@bp.route("/")
@bp.route("/title")
def title():
    return render_template("title.html")


@bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form["name"]
        password = request.form["password"]
        password2 = request.form["password2"]
        error = None
        if password != password2:
            error = "ошибка при вводе пароля"
            flash(error)
            return render_template("auth/register.html")
        user = db.session.execute(
            db.select(Users).where(Users.name == username)
        ).scalar() 
         
        
        if user is not None:
            error = "такой логин уже есть"
            flash(error)
            return render_template("auth/register.html") 
        
        if error is None:
            user = Users(name=username, password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("auth.login"))

    else:
        return render_template("auth/register.html",title="Регистрация")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('posts.list'))
    
    if request.method == "POST":

        username = request.form["name"]
        password = request.form["password"]
        user = db.session.execute(
            db.select(Users).where(Users.name == username)
        ).scalar() 
         
        
        if user is None or not check_password_hash(user.password, password):
            error = "пользователь не найден"
            flash(error)
            return render_template("title.html")
        else:
            
            session.clear()
            get_roles(user)
            login_user(user)
            session["name"] = username
            if user.settings == None:
                session["filter"] = ""
            else:
                session["filter"] = user.settings
            return redirect(url_for("posts.list"))
            
    else:
        return render_template("title.html")


@bp.route("/logout")
def logout():
    session.clear()
    logout_user()
    return redirect(url_for("auth.title"))
