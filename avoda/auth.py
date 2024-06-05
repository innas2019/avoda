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


def update_settings(s):
    id = session["_user_id"]  # user-login set parameter
    user = db.session.get(Users, int(id))
    user.settings = json.dumps(s)
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
            # временно для тестирования
            #role = db.one_or_404(db.select(Role).where(Role.name == "create_post"))
            #user.roles.append(role)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("auth.login"))

    else:
        return render_template("auth/register.html", title="Регистрация")


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
                session["filter"] = json.loads(user.settings)

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
        if  user.settings!=None and user.settings!="":
            filter = json.loads(user.settings)
            allrefs = m.get_refs()
            filterstr = filter["days"] + " дней, " + allrefs[filter["place"]]
            if filter["occupations"] != None:
                filterstr = filterstr + ", " + allrefs[filter["occupations"]]
        else:
            filterstr=None
        return render_template(
            "auth/cabinet.html", title="Личный кабинет для ", user=user, filterstr=filterstr
        )

@bp.route("/users/<int:id>", methods=["POST", "GET"])
@login_required
def list_users(id):
  roles=db.session.execute(
            db.select(Role)
        ).scalars()
  if request.method == "GET":
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
        prev_label="назад",
        next_label="вперед",
        bs_version=5,
    )
    filterstr=""
    if id == 0:
        u = Users(name="")
        
    else:
      try:
        u = [r for r in all if r.id == id]
        u = u[0]
        if  u.settings!=None and u.settings!="":
            filter = json.loads(u.settings)
            allrefs = m.get_refs()
            filterstr = filter["days"] + " дней, " + allrefs[filter["place"]]
            if filter["occupations"] != None:
                filterstr = filterstr + ", " + allrefs[filter["occupations"]]
       
      except:
        u = Users(name="")
    
    return render_template(
        "auth/users.html",
        pagination=pagination,
        title="пользователи",
        list=all,
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
        flash(u.email + " изменено")
        
        return redirect("/users/0")  

@bp.route("/users/d/<int:id>")
def delete(id):
    u = db.one_or_404(db.select(Users).where(Users.id == id))
    value=u.name
    db.session.delete(u)
    db.session.commit()
    flash(value + " удалено")
    return redirect("/users/0") 

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
        return redirect("/users/"+str(id))
