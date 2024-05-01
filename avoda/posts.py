from flask_paginate import Pagination, get_page_parameter
from flask_login import login_required
from flask import Blueprint, flash, redirect, render_template, request, url_for, session
from avoda import db
from avoda.models import Posts
from avoda import managing as m
from avoda import auth as a
from datetime import datetime, timezone
import json
from sqlalchemy import text

bp = Blueprint("posts", __name__)
s_posts = []
user = ""
count_days = "60"
len_levels = []
leng = ["en", "he", "ru"]
towns = []
o_list = []
o_kind = []
docs = []
sex = ["мужчина", "женщина"]

allrefs = {}


# объект для показа объявлений. содержит методы для преобразования текстовых значений справочников в id
class Post:
    def __init__(self, _name, _place, _phone, _text):
        self.name = _name
        self.place = _place
        self.phone = _phone
        self.text = _text
        self.len = {}  # dictionary len:level
        self.occupations = []
        self.o_kind = []
        self.sex = ""
        self.id = 0
        self.docs = []

    # функция возвращает id справочника по его значению
    def get_id_from_value(self, value):
        print(value)
        if isinstance(value, str):
            for x in allrefs:
                if allrefs[x] == value:
                    return str(x)

        else:
            new_val = []
            for v in value:
                for x in allrefs:
                    if allrefs[x] == v:
                        new_val.append(str(x))
            return new_val

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
            elif str(f).find("d") != -1:
                self.docs.append(map[f])
        print("занятость", self.o_kind)

    def get_name_by_id(self, ids):
        new_val = []
        for i in ids:
            new_val.append(allrefs[i])
        return new_val

    # функция добавляет все поля объекта из SQL
    def get_from_db(self, p):
        self.id = p.id
        if p.len != None:
            self.len = json.loads(p.len)
        if p.occupations != None:
            self.occupations = self.get_name_by_id(json.loads(p.occupations))
        if p.o_kind != None:
            self.o_kind = self.get_name_by_id(json.loads(p.o_kind))
        if p.docs != None:
            self.docs = self.get_name_by_id(json.loads(p.docs))
        print("прочитали: ", self.o_kind, self.docs)
        if p.sex != None and p.sex != "":
            self.sex = sex[p.sex]
        self.updated = p.updated
        if p.place != None and p.place != "":
            self.place = allrefs[p.place]


def create_post(n_post):
    global sex
    now = datetime.now(timezone.utc)
    new_post = Posts(
        created=now,
        updated=now,
        name=n_post.name,
        place=n_post.get_id_from_value(n_post.place),
        phone=n_post.phone,
        text=n_post.text,
        len=json.dumps(n_post.len)    
    )
    if (n_post.occupations!=""):
        new_post.occupations=json.dumps(n_post.get_id_from_value(n_post.occupations))
    if (n_post.docs!=""):
        new_post.docs=json.dumps(n_post.get_id_from_value(n_post.docs))
    if (n_post.o_kind!=""):
        new_post.o_kind=json.dumps(n_post.get_id_from_value(n_post.o_kind))
    if (n_post.sex!=""):
        new_post.sex=sex.index(n_post.sex)
    db.session.add(new_post)
    db.session.commit()
    flash(n_post.name + " добавлено")
    return "ok"


def update_post(n_post):
    global sex
    now = datetime.now(timezone.utc)
    db_post = db.one_or_404(db.select(Posts).where(Posts.id == n_post.id))
    # db_post = db.session.execute(db.select(Posts).where(Posts.id == n_post.id)).scalar()
    now = datetime.now(timezone.utc)
    db_post.updated = now
    db_post.name = n_post.name
    db_post.place = n_post.get_id_from_value(n_post.place)
    db_post.phone = n_post.phone
    db_post.text = n_post.text
    db_post.len = json.dumps(n_post.len)
    if (n_post.occupations!=""):
        db_post.occupations=json.dumps(n_post.get_id_from_value(n_post.occupations))
    if (n_post.docs!=""):
        db_post.docs=json.dumps(n_post.get_id_from_value(n_post.docs))
    if (n_post.o_kind!=""):
        db_post.o_kind=json.dumps(n_post.get_id_from_value(n_post.o_kind))
    if (n_post.sex!=""):
        db_post.sex=sex.index(n_post.sex)
  
    db.session.commit()
    flash(n_post.name + " изменено")
    return "ok"


def validation(post):
    if post.place == "":
        return False
    if post.id!=0:
        return True
    
    p = db.session.execute(
            db.select(Posts).where(Posts.phone == post.phone )
        ).scalar() 
    if p is not None:
        flash(post.phone + " такой номер уже есть")
        return False
    
    return True


# формирует условия для запроса к базе. если хоть  одно условие задано то в начале стоит and
def filters(flt):
    n_post = Post("", "", "", "")
    res = {}
    res["occupations"] = n_post.get_id_from_value(flt["oc"])
    res["place"] = n_post.get_id_from_value(flt["place"])
    res["days"] = flt["days"]
    print(res)
    return res


def filtersold(flt):
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
    global o_kind
    global docs
    global allrefs
    global sex

    # заполняем справочники
    allrefs = m.get_refs()
    len_levels = m.get_ref("levels")
    towns = m.get_ref("places")
    o_list = m.get_ref("occupations")
    o_kind = m.get_ref("conditions")
    docs = m.get_ref("documents")


# показывает список заявок
# если метод post то разбираем request.form
# это может быть фильтр или поиск


@bp.route("/list", methods=["POST", "GET"])
@login_required
def list():
    title = "Все публикации"
    if session.get("filter") != "":
        title = "Выбранные публикации"
    # в случае если задан фильтр для заявок то метод POST
    if request.method == "POST":
        session["filter"] = filters(request.form)
    
    page = request.args.get(get_page_parameter(), type=int, default=1)
    limit = 10
    # query = db.select(Posts).where(Posts.place=="Тель-Авив",Posts.len.like("%ru%"))
    if session.get("filter") != "":
        current_time = datetime.datetime.now()
        delta = current_time - datetime.timedelta(
            days=int(session.get("filter")["days"])
        )
        if session.get("filter")["occupations"] != None:
            s = '%"' + session.get("filter")["occupations"] + '"%'
            query = (
                db.select(Posts)
                .where(
                    Posts.place == session.get("filter")["place"],
                    Posts.occupations.like(s),
                    Posts.updated > delta,
                )
                .order_by(Posts.updated.desc())
            )
        else:
            query = (
                db.select(Posts)
                .where(
                    Posts.place == session.get("filter")["place"],
                    Posts.updated > delta
                )
                .order_by(Posts.updated.desc())
            )
    else:
        query = db.select(Posts).order_by(Posts.updated.desc())
    # читаем по страницам
    ps = db.paginate(query, page=page, per_page=limit, error_out=True)
    s_posts = []
    for p in ps.items:
        s_posts.append(p.id)
    session["items"]=s_posts    
    pagination = Pagination(
        page=page,
        page_per=limit,
        total=ps.total,
        display_msg="показано <b>{start} - {end}</b> {record_name} из <b>{total}</b>",
        record_name="объявлений",
        prev_label="назад",
        next_label="вперед",
        bs_version=5

    )
    return render_template(
        "posts/list.html",
        pagination=pagination,
        title=title,
        posts=ps.items,
        refs=allrefs,
    )


@bp.route("/filter/<string:p>")
@login_required
# all/set  устанавливает или сбрасывает фильтр
def filter(p):
    if p == "set":
        return render_template(
            "posts/filters.html",
            towns=towns,
            languages=leng,
            occupations=o_list,
            o_kind=o_kind,
            title="Настройки фильтра",
        )
    else:
        session["filter"] = ""
        return redirect(url_for("posts.list"))


@bp.route("/create", methods=["POST", "GET"])
@login_required
def create():
    global sex
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
            docs=docs,
            sex=sex,
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
            docs=docs,
            sex=sex,
        )


@bp.route("/post/<int:id>", methods=["GET", "POST"])
@login_required
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
            docs=docs,
            sex=sex,
        )
    else:
        ps = db.one_or_404(db.select(Posts).where(Posts.id == id))
        current_post = Post(ps.name, ps.place, ps.phone, ps.text)
        current_post.get_from_db(ps)  

        return render_template(
            "posts/post.html",
            towns=towns,
            post=current_post,
            languages=leng,
            occupations=o_list,
            o_kind=o_kind,
            levels=len_levels,
            docs=docs,
            sex=sex,
        )


@bp.route("/show/<int:id>")
@login_required
#получаем объект по номеру из списка
def show_post(id):
    s_posts=session["items"]
    if len(s_posts) == 0:
        return redirect(url_for("posts.list"))
    pstemp = s_posts[id - 1]
    # объект содержит разницу между датами
    ps = db.one_or_404(db.select(Posts).where(Posts.id == pstemp))
    p = Post(ps.name, ps.place, ps.phone, ps.text)
    p.get_from_db(ps)
    delta = datetime.today() - p.updated
    pos = id
    prev = 0
    if pos > 0:
        prev = id - 1
    next = 0
    if pos < len(s_posts) :
        next = id + 1
    return render_template(
        "posts/show_post.html",
        post=p,
        days=delta.days,
        prev=prev,
        next=next,
        current=pos,
        last=len(s_posts),
        sex=sex
    )


# для поиска по имени или телефону
@bp.route("/search")
@login_required
def search():
    return render_template("posts/search.html")

@bp.route("/del/<int:id>")
@login_required
def delete(id):
    p = db.one_or_404(db.select(Posts).where(Posts.id == id))
    value=p.phone
    db.session.delete(p)
    db.session.commit()
    flash(value + " удалено")
    return redirect("/list")  
