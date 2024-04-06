from flask_paginate import Pagination, get_page_parameter

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
    session,
    current_app,
)
from avoda import db
from avoda.models import Posts
from avoda import managing as m
from avoda import auth as a
import datetime
import json


bp = Blueprint("posts", __name__)
s_posts = []
user = ""
count_days = "60"
len_levels = []
leng = ["en", "he", "ru"]
towns = []
o_list = []
o_kind = ["полная", "частичная"]
current_post = None  # frontend ob


class Post:
    def __init__(self, _name, _place, _phone, _text):
        self.name = _name
        self.place = _place
        self.phone = _phone
        self.text = _text
        self.len = {}
        self.occupations = []
        self.o_kind = []
        self.sex = ""
        self.id = 0
        self.created = datetime.date.today()
        self.updated = datetime.date.today()

    # функция возвращает список языков для показа во вью
    def get_len(self):
        conv = str(self.len).replace("{", " ").replace("}", " ")
        return conv.replace("'", " ")

    # функция возвращает значение атрибута по его имени
    def get_atr_by_name(self, source):
        dataSource = getattr(self, source)
        return dataSource

    # функция заполняет поля объекта из формы
    def get_from_form(self, map):
        for f in map.keys():
            # для языков из списка
            if str(f).find("len") != -1 and str(f).find("level") == -1:
                s = "len_level" + str(map[f])
                value = str(map[s])
                self.len.update({map[f]: value})
            elif str(f).find("oc") != -1:
                self.occupations.append(map[f])
            elif str(f).find("ok") != -1:
                self.o_kind.append(map[f])
            elif str(f).find("sex") != -1:
                self.sex = map[f]

    # функция добавляет все поля объекта из SQL
    def get_from_db(self, p):
        self.id = p.id
        if p.len!=None:
           self.len = json.loads(p.len)
        if p.occupations!=None:
           self.occupations = json.loads(p.occupations)
        if p.o_kind!=None:
            self.o_kind = json.loads(p.o_kind)
        self.sex = p.sex
        self.updated = p.updated


def create_post(n_post):
    new_post = Posts(
        created=n_post.created,
        updated=n_post.updated,
        name=n_post.name,
        place=n_post.place,
        phone=n_post.phone,
        text=n_post.text,
        len=json.dumps(n_post.len),
        occupations=json.dumps(n_post.occupations),
        o_kind=json.dumps(n_post.o_kind),
        sex=n_post.sex,
    )
    db.session.add(new_post)
    db.session.commit()
    flash(n_post.name + " добавлено")
    return "ok"


def update_post(n_post):
    db_post = db.one_or_404(db.select(Posts).where(Posts.id == n_post.id))
    #db_post = db.session.execute(db.select(Posts).where(Posts.id == n_post.id)).scalar()
    db_post.updated = n_post.updated
    db_post.name = n_post.name
    db_post.place = n_post.place
    db_post.phone = n_post.phone
    db_post.text = n_post.text
    db_post.len = json.dumps(n_post.len)
    db_post.occupations = json.dumps(n_post.occupations)
    db_post.o_kind = json.dumps(n_post.o_kind)
    db_post.sex = n_post.sex
    db.session.commit()
    flash(n_post.name + " изменено")
    return "ok"


def validation(post):
    if post.place == "":
        return False
    return True


# формирует условия для запроса к базе. если хоть  одно условие задано то в начале стоит and
def filters(flt):
    conditions = ""
    len = ""
    oc = ""
    global count_days
    count_days = flt["count_days"]
    for f in flt.keys():
        if str(f).find("len_") != -1:
            if len == "":
                len = "len like "
            len_key = str(f).split("_")
            len = len + "'%" + len_key[1] + "%'"
            conditions = conditions + " and " + len
        if str(f).find("oc") != -1:
            if oc == "":
                oc = "occupations like "
            oc = oc + "'%" + flt[f] + "%'"
            conditions = conditions + " and " + oc
        if str(f) == "place" and flt[f] != "-":
            place = "place =" + "'" + flt[f] + "'"
            conditions = conditions + " and " + place
        if str(f).find("sex") != -1:
            sex = "sex= '" + flt[f] + "'"
            conditions = conditions + " and " + sex
        if str(f) == "permanent":
            a.update_settings(session["filter"])

    return conditions


@bp.before_app_request
def load_ref():
    global len_levels
    global towns
    global o_list

    # заполняем справочники
    len_levels = m.get_ref("levels")
    towns = m.get_ref("places")
    o_list = m.get_ref("occupations")


@bp.route("/list", methods=["POST", "GET"])
def list():
    # список заявок
    title = "Все публикации"
    global s_posts
    global current_post
    current_post = None
    page = request.args.get(get_page_parameter(), type=int, default=1)
    limit = 10
    query = db.select(Posts).order_by(Posts.updated.desc())
    # читаем по страницам
    ps = db.paginate(query, page=page, per_page=limit, error_out=True)
    s_posts = ps.items
    pagination = Pagination(page=page, page_per=limit, total=ps.total)
    return render_template(
        "posts/list.html",
        pagination=pagination,
        title=title,
        posts=s_posts,
        user=user,
    )


@bp.route("/filter/<string:p>")
# all/set
def filter(p):
    if p == "set":
        return render_template(
            "posts/filters.html",
            towns=towns,
            languages=leng,
            occupations=o_list,
            o_kind=o_kind,
        )
    else:
        session["filter"] = ""
        return redirect(url_for("posts.list"))


@bp.route("/create", methods=["POST", "GET"])
def create():
    if request.method == "POST":
        form = request.form
        n_post = Post(form["name"], form["place"], form["phone"], form["text"])
        n_post.get_from_form(form)
        if validation(n_post):
            if create_post(n_post):
                flash("Запись добавлена!")
                return redirect(url_for("posts.list"))

        return render_template(
            "posts/post.html",
            towns=towns,
            post=n_post,
            languages=leng,
            occupations=o_list,
            o_kind=o_kind,
            levels=len_levels,
        )
    else:
        p = Post("", "", "", "")
        return render_template(
            "posts/post.html",
            towns=towns,
            post=p,
            languages=leng,
            occupations=o_list,
            o_kind=o_kind,
            levels=len_levels,
        )


@bp.route("/post/<int:id>", methods=["GET", "POST"])
def post(id):
    global current_post
    if request.method == "POST":
        form = request.form
        n_post = Post(form["name"], form["place"], form["phone"], form["text"])
        n_post.id = id
        n_post.get_from_form(form)
        if validation(n_post):
            if update_post(n_post):
                return redirect(url_for("posts.list"))

        return render_template(
            "posts/post.html",
            towns=towns,
            post=n_post,
            languages=leng,
            occupations=o_list,
            o_kind=o_kind,
            levels=len_levels,
        )
    else:

        return render_template(
            "posts/post.html",
            towns=towns,
            post=current_post,
            languages=leng,
            occupations=o_list,
            o_kind=o_kind,
            levels=len_levels,
        )


@bp.route("/show/<int:id>")
def show_post(id):
    global current_post
    ps = s_posts[id - 1]
    # объект содержит разницу между датами
    p = Post(ps.name, ps.place, ps.phone, ps.text)
    p.get_from_db(ps)
    current_post = p
    delta = datetime.datetime.today() - p.updated
    pos = id
    prev = 0
    if pos > 0:
        prev = id - 1
    next = 0
    if pos < len(s_posts) - 1:
        next = id + 1
    return render_template(
        "posts/show_post.html",
        post=p,
        days=delta.days,
        prev=prev,
        next=next,
        current=pos + 1,
        last=len(s_posts),
    )


@bp.route("/search")
def search():
    return render_template("posts/search.html")
