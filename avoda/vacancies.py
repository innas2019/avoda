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

def create_post(post, res):
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
        )
        db.session.add(new_post)
        msg = (
            post.name
            + ", спасибо за заполнение вакансии. После проверки она появится на нашем сайте. "
        )

    else:
        new_post = db.one_or_404(db.select(Vacancies).where(Vacancies.id == post.id))
        if res != None:
            new_post.result = res
            new_post.created = now
        msg = post.phone + " " + msg
    db.session.commit()
    flash(msg)

    return True

@bp.route("/vacs")
def list_vacs():
    query=None
    if ("roles" in session) and (session["roles"].count("create_roles")) > 0:
     query = (
        db.select(Vacancies)
        .where(Vacancies.result != 0)
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
        n_post = Vacancy("", form["place"], form["phone"], form["text"],form["salary"],None)
        n_post.id = id
        n_post.get_from_form(form)
        if "res" in form.keys():
            n_post.result = form["res"]
        if not create_post(n_post):
            return render_template(
                "vacs/vac.html", towns=towns, post=n_post, place=n_post.place,occupations=o_list
            )

        return redirect("/vacs")

    else:
        # method get
        if id == 0:
            ps = Vacancy(
                "",
                "",
                "",
                pattern,0,None
            )
            place = ""
        else:
            ps = db.one_or_404(db.select(Vacancies).where(Vacancies.id == id))
            place = allrefs[ps.place]

        return render_template(
            "vacs/vac.html", towns=towns, post=ps, place=place, results=results, pattern=pattern,occupations=o_list
        )
