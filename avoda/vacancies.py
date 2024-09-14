from flask_paginate import Pagination, get_page_parameter
from flask_login import login_required
from flask import Blueprint, flash, redirect, render_template, request, url_for, session
from avoda import db
from avoda.models import Posts, Vacancies
from avoda.posts import show_in_view,Post
from avoda import managing as m
from datetime import datetime, timezone, timedelta
import json
# from flask import jsonify
from sqlalchemy import and_, or_, desc


bp = Blueprint("vacs", __name__)

user = ""
towns = []
o_list = []
hierarchy = {}
allrefs = {}
pattern = "Требуются сотрудники в ....  , смены ... Языки: иврит - разговорный. Другие требования... "
#0 отклоненные 1 принятые  2 не актуальные
results = ["отклонено", "принято","не актуально"]

class Vacancy(Post):
    def __init__(self, _name, _place, _phone, _text,_salary,_result):
     Post.__init__(self, _name, _place, _phone, _text)
     self.salary=_salary
     self.result=_result
   
    def get_vacs_from_db(self, p):
        self.id = p.id
        if p.contacts!=None:
            self.contacts=p.contacts
        if p.occupations != None:
            self.occupations = self.get_name_by_id(json.loads(p.occupations))
        if p.place != None and p.place != "":
            self.place = allrefs[p.place]

    
@bp.before_app_request
def load_ref():
    global towns
    global allrefs
    global hierarchy
    global o_list
    # заполняем справочники
    allrefs = m.get_refs()
    towns = m.get_ref("places")
    towns.sort()
    o_list = m.get_ref("occupations")
    hierarchy = m.get_hier_for_search()

def create_post(post):
    now = datetime.now(timezone.utc)
    msg = "сохранено"
    check=True
    if post.id == 0:
        if pattern == post.text:
            msg="внесите свои данные в текст вакансии"
            check = False

        if "..."  in post.text:
            msg="замените точки на информацию о вакансии"
            check = False

        if int(post.salary)<30:
            msg="зарплата не менее 30 шек/час"
            check = False

        if  not check:
            flash(msg)
            return False

        new_post = Vacancies(
            created=now,
            place=post.get_id_from_value(post.place),
            phone=post.phone,
            text=post.text,
            contacts=post.contacts,
            name=post.name,
            salary=post.salary,
            result=post.result)
        if post.occupations != "":
                new_post.occupations = json.dumps(post.get_id_from_value(post.occupations))       
                            
        db.session.add(new_post)
        msg = (
            post.name
            + ", спасибо за заполнение вакансии. После проверки она появится на нашем сайте. "
        )

    else:
        ps = db.one_or_404(db.select(Vacancies).where(Vacancies.id == post.id))
        ps.place=post.get_id_from_value(post.place)
        ps.phone=post.phone
        ps.text=post.text
        ps.contacts=post.contacts
        ps.name=post.name
        ps.salary=post.salary
        ps.result=post.result
        if post.occupations != "":
                ps.occupations = json.dumps(post.get_id_from_value(post.occupations))       
        msg = post.phone + " " + msg
    db.session.commit()
    flash(msg)

    return True

@bp.route("/vacs")
def list_vacs():
    query=None
    if ("roles" in session) and (session["roles"].count("create_post")) > 0:
     query = (
        db.select(Vacancies)
        .where((Vacancies.result == None) | (Vacancies.result != 0))
        .order_by(Vacancies.result,desc(Vacancies.id))
      )
    else:
      query = (
        db.select(Vacancies)
        .where(Vacancies.result == 1)
        .order_by(Vacancies.result,desc(Vacancies.id))
      )  
    # читаем по страницам
    limit = 20

    page = request.args.get(get_page_parameter(), type=int, default=1)
    ps = db.paginate(query, page=page, per_page=limit, error_out=True)
    all = ps.items
    pagination = Pagination(
        page=page,
        per_page=limit,
        total=ps.total,
        display_msg="показано <b>{start} - {end}</b> {record_name} из <b>{total}</b>",
        record_name="записей",
        prev_label="<<",
        next_label=">>",
        bs_version=4,
    )

    return render_template(
        "vacs/vacslist.html",
        pagination=pagination,
        title="Вакансии",
        list=all,
        refs=allrefs,
        results=results,
    )

@bp.context_processor
def utility_processor():

    return dict(show_in_view=show_in_view)

@bp.route("/vac/<int:id>", methods=["GET", "POST"])
def post(id):
    if request.method == "POST":
        form = request.form
        n_post = Vacancy(form["name"], form["place"], form["phone"], form["text"],form["salary"],None)
        n_post.id = id
        n_post.get_from_form(form)
        if "res" in form.keys():
            n_post.result = form["res"]
        n_post.salary=form["salary"]
        if "res" in form.keys():
          n_post.result=form["res"]
        
        if not create_post(n_post):
            return render_template(
                "vacs/vac.html", towns=towns, post=n_post, place=n_post.place,results=results, occupations=o_list, editmode=True
            )
    
        return redirect("/vacs")

    else:
        # method get
        editmode=False
        if id == 0:
            p = Vacancy(
                "",
                "",
                "",
                pattern,0,None
            )
            place = ""
            editmode=True
        else:
            ps = db.one_or_404(db.select(Vacancies).where(Vacancies.id == id))
            p = Vacancy(ps.name, ps.place, ps.phone, ps.text,ps.salary,ps.result)
            p.get_vacs_from_db(ps)
            #            place = allrefs[ps.place]
            #        if p.occupations != None:
            #self.occupations = self.get_name_by_id(json.loads(p.occupations))
            if ("roles" in session) and (session["roles"].count("create_post")) > 0: 
                editmode=True
        return render_template(
            "vacs/vac.html", towns=towns, post=p, place=p.place, results=results, pattern=pattern,occupations=o_list,editmode=editmode
        )
