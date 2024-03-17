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
from avoda.db import get_db
from avoda import managing as m
from avoda import auth as a
import datetime
import json


bp = Blueprint("posts", __name__)

posts = []
user = ""
count_days = "30"
len_levels = []
leng = ["en", "he", "ru"]
towns = []
o_list = []
o_kind = ["полная", "частичная"]


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
        self.id = p["id"]
        self.len = json.loads(p["len"])
        self.occupations = p["occupations"]
        self.o_kind = p["o_kind"]
        self.sex = p["sex"]
        self.updated = p["updated"]


def create_post(n_post):
    db = get_db()
    try:
        db.execute(
            "INSERT INTO post (created, updated, name, place, phone, text, len, occupations, o_kind, sex) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                n_post.created,
                n_post.updated,
                n_post.name,
                n_post.place,
                n_post.phone,
                n_post.text,
                json.dumps(n_post.len),
                str(n_post.occupations),
                str(n_post.o_kind),
                n_post.sex,
            ),
        )
        db.commit()
    except db.Error as e:
        flash(e)
        return e
    flash(n_post.name + " добавлено")
    return "ok"


def update_post(n_post):
    db = get_db()
    len = ""
    try:
        len = json.dumps(n_post.len)
    except json.Error as e:
        print(e)

    try:
        db.execute(
            "update post set updated=?, name=?, place=?, phone=?, text=?, len=?, occupations=?, o_kind=?, sex=? where id=?",
            (
                n_post.updated,
                n_post.name,
                n_post.place,
                n_post.phone,
                n_post.text,
                len,
                str(n_post.occupations),
                str(n_post.o_kind),
                n_post.sex,
                n_post.id,
            ),
        )
        db.commit()
    except db.Error as e:
        flash(e)
        return e
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
    if session.get("filter") != "":
        title = "Выбранные публикации"
    # в случае если задан фильтр для заявок то метод POST
    if request.method == "POST":
        session["filter"] = filters(request.form)
        # session['days']=count_days

    db = get_db()
    try:
        conditions = (
            "where julianday() - julianday(updated)<"
            + count_days
            + session.get("filter")
        )
        posts.clear()
        page = request.args.get(get_page_parameter(), type=int, default=1)
        limit = 10
        offset = page * limit - limit
        res = db.execute("select count(id) as c from post " + conditions).fetchone()
        total = res["c"]
        ps = db.execute(
            "select * from post " + conditions + " limit ? offset ?", (limit, offset)
        ).fetchall()

        for p in ps:
            np = Post(p["name"], p["place"], p["phone"], p["text"])
            np.get_from_db(p)
            posts.append(np)
        pagination = Pagination(page=page, page_per=limit, total=total)
        return render_template(
            "posts/list.html",
            pagination=pagination,
            title=title,
            posts=posts,
            user=user,
        )
    except db.Error as e:
        return e


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

        for p in posts:
            if id == p.id:
                return render_template(
                    "posts/post.html",
                    towns=towns,
                    post=p,
                    languages=leng,
                    occupations=o_list,
                    o_kind=o_kind,
                    levels=len_levels,
                )


@bp.route("/show/<int:id>")
def show_post(id):
    for p in posts:
        if id == p.id:
            # преобразование даты в datetime
            d = datetime.datetime.strptime(p.updated, "%Y-%m-%d")
            # объект содержит разницу между датами
            delta = datetime.datetime.today() - d
            pos = posts.index(p)
            prev = 0
            if pos > 0:
                prev = posts[pos - 1].id
            next = 0
            if pos < len(posts) - 1:
                next = posts[pos + 1].id
            return render_template(
                "posts/show_post.html",
                post=p,
                days=delta.days,
                prev=prev,
                next=next,
                current=pos + 1,
                last=len(posts),
            )


@bp.route("/search")
def search():
    return render_template("posts/search.html")
