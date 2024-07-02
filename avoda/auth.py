from flask import Blueprint, flash, redirect, render_template, request, url_for, session
from flask_login import current_user, login_user, logout_user, login_required
from flask_paginate import Pagination, get_page_parameter
from werkzeug.security import check_password_hash, generate_password_hash
from avoda import db
from flask import current_app
from avoda.models import Users, Role
import logging
import json
from avoda import managing as m
from avoda.posts import Post

def get_roles(user):
    session["roles"] = []
    for r in user.roles:
        session["roles"].append(r.name)


def add_roles(username, rolename):
    user = db.session.execute(db.select(Users).where(Users.name == username)).scalar()
    if user is None:
        error = username + " не найден"
        flash(error)
        return False

    role = db.one_or_404(db.select(Role).where(Role.name == rolename))
    if role is None:
        error = rolename + " не найдена"
        flash(error)
        return False

    user.roles.append(role)
    db.session.commit()
    return True


def update_settings(id,s):
    user = db.session.get(Users, int(id))
    if s=="":
        user.settings=s
    else:
        user.settings = json.dumps(s)
    db.session.commit()
    flash(" Изменены настройки пользователя "+ user.name)

def get_user_settings(user):
        filterstr=""
        if  user.settings!=None and user.settings!="":
            filter = json.loads(user.settings)
            allrefs = m.get_refs()
            filterstr = filter["days"] + " дней, " + allrefs[filter["place"]]
            if filter["occupations"] != None:
                filterstr = filterstr + ", " + allrefs[filter["occupations"]]
        
        return filterstr    

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
        if password == "11111111" or password=="12345678":
            error = "используйте более сложный пароль"
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
            l = current_app.logger
            l.setLevel(logging.INFO)
            l.info(username + " registered")
            session.clear()
            login_user(user)
            session["name"] = username
            session["roles"] = []
            session["filter"] = ""  
            session["search"] = "" 
            #return redirect(url_for("auth.login"))
            return render_template("auth/register.html", title=" Спасибо за регистрацию на нашем сайте!",info=True)

    else:
        return render_template("auth/register.html", title="Регистрация",info=False)


@bp.route("/login", methods=["GET", "POST"])
def login():
    #if current_user.is_authenticated:
    #    return redirect(url_for("posts.list"))

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
            if user.settings == None or user.settings =="":
                session["filter"] = ""
            else:
                try:
                  session["filter"] = json.loads(user.settings)
                except:
                  session["filter"] = ""  
                  user.settings=""
                  db.session.commit()        
            
            session["search"] = "" 
            l = current_app.logger
            l.setLevel(logging.INFO)
            l.info(username + " login")
            return redirect(url_for("posts.list"))

    else:
        return render_template("title.html")


@bp.route("/logout")
def logout():
    session.clear()
    logout_user()
    return redirect(url_for("auth.title"))

@bp.route("/cabinet", methods=["GET", "POST"])
@login_required
def cabinet():
    if request.method == "POST":
        # для любого юзера
        if "newsletter" in request.form.keys():
            issend=1
        else:
            issend=0    
        email = request.form["email"]           
        user = db.session.execute(
            db.select(Users).where(Users.name == request.form["name"])
        ).scalar()
        user.email = email
        user.issend = issend
        if "clean" in request.form.keys():
            user.settings=""
        db.session.commit()
        flash(user.name + " настройки  изменены")
        session["filter"] = ""
        return redirect(url_for("posts.list"))
    else:
        # пока для текущего юзера
        
        user = db.session.execute(
            db.select(Users).where(Users.name == session["name"])
        ).scalar()
        filterstr=get_user_settings(user)
        return render_template(
            "auth/cabinet.html", title="Личный кабинет для ", user=user, filterstr=filterstr
        )


@bp.route("/users/<directions>")
@login_required

def list_users(directions):
    if session['roles'].count("adminisrators")==0:
      return redirect("/list")  
    
    if directions=="bydate":
        query = db.select(Users).order_by(Users.id.desc())
    else: 
        query = db.select(Users).order_by(Users.name)
    # читаем по страницам
    limit = 10
    if id == 0:
        u = Users(name="")
    page = request.args.get(get_page_parameter(), type=int, default=1)
    ps = db.paginate(query, page=page, per_page=limit, error_out=True)
    all=ps.items
    pagination = Pagination(
        page=page,
        page_per=limit,
        total=ps.total,
        display_msg="показано <b>{start} - {end}</b> {record_name} из <b>{total}</b>",
        record_name="записей",
        prev_label="<<",
        next_label=">>",
        bs_version=4,
    )
    
    return render_template(
        "auth/users.html",
        pagination=pagination,
        title="пользователи",
        list=all        
    )
 

@login_required

@bp.route("/users/d/<int:id>")
def delete(id):
    if session['roles'].count("adminisrators")==0:
      return redirect("/list")  
    u = db.one_or_404(db.select(Users).where(Users.id == id))
    value=u.name
    db.session.delete(u)
    db.session.commit()
    flash(value + " удалено")
    return redirect("/users/0") 

@login_required

#для сохранения фильтра администратором
@bp.route("/users/f/<int:id>", methods=["POST", "GET"])
def save_filter(id):
    if request.method == "POST":
        flt=request.form
        n_post = Post("", "", "", "")
        res = {}
        res["occupations"] = n_post.get_id_from_value(flt["oc"])
        res["place"] = n_post.get_id_from_value(flt["place"])
        res["days"] = flt["days"]
        user = db.session.get(Users, int(id))
        user.settings = json.dumps(res)
        db.session.commit()
        return redirect("/users/byname")

@bp.route("/info")
def info():
    return render_template("auth/register.html", title=" О системе",info=True)


@bp.route("/user/<int:id>", methods=["POST", "GET"])
@login_required

def edit_user(id):
    if session['roles'].count("adminisrators")==0:
      return redirect("/list")  
    
    roles=db.session.execute(
            db.select(Role)
        ).scalars()

    if request.method == "GET":
     try:
        u = db.session.get(Users, int(id))
        filterstr=get_user_settings(u)
        #   u = [r for r in all if r.id == id]        u = u[0]     
     except:
        filterstr=""
    
     return render_template(
        "auth/edituser.html",
        r=u,
        roles=roles,
        filterstr=filterstr
    )
    else:
        #если post изменяем запись
        r=roles.all()
        email=""
        if "email" in request.form.keys():
         email = request.form["email"]
        if "newsletter" in request.form.keys():
            issend=1
        else:
            issend=0  
            
        #проверка на роли. если их состав изменился, то перезаписываем
        uroles=[]
        if "rs_adminisrators" in request.form.keys():
            uroles.append(r[0])
        if "rs_create_post" in request.form.keys():
            uroles.append(r[1])  
        u = db.one_or_404(db.select(Users).where(Users.id == id))
        u.email=email
        u.issend =issend   
        u.roles=uroles
        db.session.commit()    
        flash(u.name + " изменено")
        
        return redirect("/users/byname") 