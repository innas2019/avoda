from flask_paginate import Pagination, get_page_parameter
from flask_login import login_required
from flask import Blueprint, flash, redirect, render_template, request, url_for, session
from avoda import db
from avoda.models import Posts, Users
from avoda import managing as m
from avoda import auth as a
from datetime import datetime, timezone, timedelta
import json
from flask import jsonify
from sqlalchemy import and_, or_

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
hierarchy={}
allrefs = {}


# объект для показа объявлений. содержит методы для преобразования текстовых значений справочников в id
class Post:
    def __init__(self, _name, _place, _phone, _text):
        self.name = _name
        self.place = _place
        self.phone = _phone
        self.contacts=""
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
        conv = conv.replace("'", " ")
        conv = conv.replace(" :", ":")
        return conv.replace(" ,", ",")
        

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
            elif str(f).find("contacts") != -1:
                self.contacts=map[f]  

    def get_name_by_id(self, ids):
        new_val = []
        for i in ids:
            new_val.append(allrefs[i])
        return new_val

    def transform_len_by_id(self, len):
        for x in len.keys():
            if len[x] in allrefs:
                len[x] = allrefs[len[x]]

        return len

    # функция добавляет все поля объекта из SQL
    def get_from_db(self, p):
        self.id = p.id
        if p.contacts!=None:
            self.contacts=p.contacts
        if p.len != None:
            self.len = self.transform_len_by_id(json.loads(p.len))
        if p.occupations != None:
            self.occupations = self.get_name_by_id(json.loads(p.occupations))
        if p.o_kind != None:
            self.o_kind = self.get_name_by_id(json.loads(p.o_kind))
        if p.docs != None:
            self.docs = self.get_name_by_id(json.loads(p.docs))
        if p.sex != None and p.sex != "":
            self.sex = sex[p.sex]
        self.updated = p.updated
        if p.place != None and p.place != "":
            self.place = allrefs[p.place]

    def transform_len_to_id(self):
        for x in self.len.keys():
            value = self.get_id_from_value(self.len[x])
            if value != None:
                self.len[x] = self.get_id_from_value(self.len[x])
        return self.len


# для показа рода занятий  из списка постов
@bp.context_processor
def utility_processor():

    def show_in_view(s):
        if s != None:
            res = ""
            ids = json.loads(s)
            for i in ids:
                res = res + " " + allrefs[i]
            return res
        return ""

    return dict(show_in_view=show_in_view) 

# для проверки номера телефона при создании поста
@bp.route("/check")
def check_phone():
    phone = request.args.get("phone", 0, type=str)
    if phone == "":
        return jsonify(result="сначала введите номер")

    query = db.select(Posts).where(Posts.phone.like("%" + phone))
    res = db.session.execute(query).scalar()
    if res is not None:
        return jsonify(result="такой номер уже есть")
    else:
        return jsonify(result="такого номера нет! можно продолжать")


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
        contacts=n_post.contacts,
        len=json.dumps(n_post.transform_len_to_id()),
    )
    if n_post.occupations != "":
        new_post.occupations = json.dumps(n_post.get_id_from_value(n_post.occupations))
    if n_post.docs != "":
        new_post.docs = json.dumps(n_post.get_id_from_value(n_post.docs))
    if n_post.o_kind != "":
        new_post.o_kind = json.dumps(n_post.get_id_from_value(n_post.o_kind))
    if n_post.sex != "":
        new_post.sex = sex.index(n_post.sex)
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
    db_post.contacts=n_post.contacts
    db_post.len = json.dumps(n_post.transform_len_to_id())
    if n_post.occupations != "":
        db_post.occupations = json.dumps(n_post.get_id_from_value(n_post.occupations))
    if n_post.docs != "":
        db_post.docs = json.dumps(n_post.get_id_from_value(n_post.docs))
    if n_post.o_kind != "":
        db_post.o_kind = json.dumps(n_post.get_id_from_value(n_post.o_kind))
    if n_post.sex != "":
        db_post.sex = sex.index(n_post.sex)

    db.session.commit()
    flash(n_post.name + " изменено")
    return "ok"

#create title str from map
def show_title(flt):
  try:
    s = "Выбранные за "  + flt["days"]  + " дней: "
    
    if flt["place"] != None:
        s = s + allrefs[flt["place"]]+", "
    
    if len(flt["occupations"])>0:
        s=s+"профессии: "
        for oc in flt["occupations"]:
            s = s + allrefs[oc]+", "
    
    return s[:len(s)-2]  
  except:
      return "Выбранные"  
def validation(post):
    
    if post.id != 0:
        return True

    if (post.phone !=""):
        p = db.session.execute(db.select(Posts).where(Posts.phone == post.phone)).scalar()
        if p is not None:
            flash(post.phone + " такой номер уже есть")
            return False

    if (post.phone =="") and (post.contacts  ==""):
        flash(" нужно заполнить телефон или контакт")
        return False
    
    return True

# формирует запрос из фильтра для списка постов и для рассылки.
def create_query(filter, days):    
    global hierarchy
    current_time = datetime.now()
    delta = current_time - timedelta(days=days)
    query = db.session.query(Posts)
    filter_conditions = []
    oc_conditions = []
    if filter != "":
        if filter["place"]!= None:
            places=[filter["place"]]
            place=int(filter["place"])
            #hierarchy for place
            if hierarchy.get(place) != None:
                places.extend(hierarchy[place])

            filter_conditions.append(Posts.place.in_(places))
    
        #get occupations value
        if filter["occupations"]!= None:
            for o in filter["occupations"]:
                s = '%"' + o + '"%' 
                oc_conditions.append(Posts.occupations.like(s))
        
            filter_conditions.append(or_(*oc_conditions))
        
    filter_conditions.append(Posts.updated > delta)
    query = query.filter(and_(*filter_conditions)).order_by(Posts.updated.desc())
    return query

# формирует фильтр из формы
def filters(flt):
    n_post = Post("", flt["place"], "", "")
    n_post.get_from_form(flt)
    res = {}
    int_days=0
    res["occupations"] = []
    for oc in n_post.occupations:
      res["occupations"].append(n_post.get_id_from_value(oc))
    res["place"] = n_post.get_id_from_value(n_post.place)
    res["days"] = flt["days"]
    try:
      int_days=int(res["days"])
     
    except: 
        error = "задано недопустимое количество дней, установлено 30"
        flash(error)
        res["days"] ="30"
    
    if int_days<1 or int_days>100:
        error = "задано недопустимое количество дней, установлено 30"
        flash(error)
        res["days"] = "30"
    
    return res

@bp.before_app_request
def load_ref():
    global len_levels
    global towns
    global o_list
    global o_kind
    global docs
    global allrefs
    global sex
    global hierarchy
    # заполняем справочники
    allrefs = m.get_refs()
    len_levels = m.get_ref("levels")
    towns = m.get_ref("places")
    towns.sort()
    o_list = m.get_ref("occupations")
    o_list.sort()
    o_kind = m.get_ref("conditions")
    docs = m.get_ref("documents")
    hierarchy=m.get_hier_for_search()


# показывает список заявок
# если метод post то разбираем request.form
# это может быть фильтр или поиск


@bp.route("/list", methods=["POST", "GET"])
@login_required
def list():
    title_str = "Все объявления"
    if session.get("filter") != "":
        title_str = "Выбранные "
    # в случае если задан фильтр для заявок то метод POST
    if request.method == "POST":
        session["filter"] = filters(request.form)
        if "permanent" in request.form.keys():
            a.update_settings(0,session["filter"])
    
    page = request.args.get(get_page_parameter(), type=int, default=1)
    limit = 10
    if session.get("filter") != "":
        query = create_query(session.get("filter"), int(session.get("filter")["days"]))
        title_str = show_title(session.get("filter"))
        
    else:
        query = db.select(Posts).order_by(Posts.updated.desc())
    #search
    phone=session["search"]
    if phone !="":
        query = (
            db.select(Posts)
            .where(Posts.phone.like("%" + phone+"%"))
            .order_by(Posts.updated.desc())
        )
        title_str = "Поиск по номеру "+phone      

    # читаем по страницам
    ps = db.paginate(query, page=page, per_page=limit, error_out=True)
    session["page"] = page
    s_posts = []
    for p in ps.items:
        s_posts.append(p.id)

    session["items"] = s_posts
    msg = "показано {record_name} с <b>{start} по {end}</b> "
    if session["roles"].count("adminisrators") > 0:
        msg = msg + " из <b>{total}</b>"
    pagination = Pagination(
        page=page,
        page_per=limit,
        total=ps.total,
        display_msg=msg,
        record_name="объявлений",
        prev_label="<<",
        next_label=">>",
        bs_version=5,
    )
    return render_template(
        "posts/list.html",
        pagination=pagination,
        title=title_str,
        posts=ps.items,
        refs=allrefs,
    )


@bp.route("/filter/<string:p>")
@login_required
# all/set  устанавливает или сбрасывает фильтр
#set + параметр id исполььзуется для редактирования профиля администратором
#параметр all+name сбрасывает постоянный фильтр
#params: ?id=12&...”
def filter(p):
  session["search"]=""
  url_params = request.args 
  id=""
  if 'id' in url_params: 
    id=url_params['id']
  
  if p == "set":
      if id=="":
        user = db.session.execute(
            db.select(Users).where(Users.name == session["name"])
        ).scalar()
        fstr=a.get_user_settings(user)
        return render_template(
            "posts/filters.html",
            towns=towns,
            languages=leng,
            occupations=o_list,
            o_kind=o_kind,
            title="Настройки фильтра",
            id=0,
            filterstr=fstr
        )
      
      else:
        user = db.session.execute(
            db.select(Users).where(Users.id == str(id))
        ).scalar()
        fstr=a.get_user_settings(user)
        return render_template(
            "posts/filters.html",
            towns=towns,
            languages=leng,
            occupations=o_list,
            o_kind=o_kind,
            title="Настройки фильтра для "+user.name,
            id=id,
            filterstr=fstr)

  if p == "all":
    if id=="":
        session["filter"] = ""
        return redirect(url_for("posts.list"))
    else:
        session["filter"] = ""
        a.update_settings(id,"")
        return redirect("/filter/set?id="+id)
    
    

@bp.route("/create", methods=["POST", "GET"])
@login_required
def create():
    global sex
    if session['roles'].count("adminisrators")==0:
      return redirect("/list")  
    
    if request.method == "POST":
        form = request.form
        print(form["place"])
        n_post = Post(form["name"], form["place"], form["phone"], form["text"])
        n_post.get_from_form(form)
        if validation(n_post):
            if create_post(n_post):
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
        p = Post("N/A", "", "", "")
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
# получаем объект по номеру из списка
def show_post(id):
    s_posts = session["items"]
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
    if pos < len(s_posts):
        next = id + 1
    return render_template(
        "posts/show_post.html",
        post=p,
        days=delta.days,
        prev=prev,
        next=next,
        current=pos,
        last=len(s_posts),
        sex=sex,
    )


# для поиска по имени или телефону
@bp.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "POST":
      phone = request.form["phone"]
      session["search"] = phone
    else:
        session["search"] = ""  
    
    return redirect(url_for("posts.list"))

@bp.route("/del/<int:id>")
@login_required
def delete(id):
    p = db.one_or_404(db.select(Posts).where(Posts.id == id))
    value = p.phone
    db.session.delete(p)
    db.session.commit()
    flash(value + " удалено")
    return redirect("/list")
