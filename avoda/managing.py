from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    session, jsonify
)
from avoda import db
from avoda.models import Refs,Users,Vacancies,Preposts
from flask_login import login_required
from flask_paginate import Pagination, get_page_parameter
from datetime import datetime, timedelta

allrefs = {}


# читаем все справочники потом с учетом выбранного языка
def get_refs():
    global allrefs
    ps = db.session.execute(db.select(Refs)).scalars()
    allrefs = ps.all()
    res = {}
    for p in allrefs:
        res[str(p.id)] = p.value
    return res


# читаем все справочники
def get_ref(name):
    global allrefs
    res = []
    if not allrefs:
        ps = db.session.execute(db.select(Refs)).scalars()
        allrefs = ps.all()
    for p in allrefs:
        if p.name == name:
            res.append(p.value)
    return res

#hierarchy
def get_hier_for_search():
    global allrefs
    res = {}  
    for p in allrefs:
        if p.levels!=[]:
            res[p.id] = ([str(x.id) for x in list(p.levels)])
    return res

bp = Blueprint("mng", __name__)
len = []
towns = []
o_list = []
o_kind = []
docs = []


# функция для показа всех записей справочника
@bp.route("/refs/<int:id>", methods=["POST", "GET"])
@login_required

def refs(id):
  if session['roles'].count("adminisrators")==0:
      return redirect("/list")  
  ref = None
  if request.method == "GET":
    refs_name = []
    res = db.session.query(Refs.name).group_by(Refs.name)
    # Execute the statement
    results = res.all()
    for name in results:
        refs_name.append(name[0])
    
    query = db.select(Refs).order_by(Refs.name,Refs.value)
    # читаем по страницам
    limit = 15
    if id == 0:
        ref = Refs(name="", value="")
    page = request.args.get(get_page_parameter(), type=int, default=1)
    ps = db.paginate(query, page=page, per_page=limit, error_out=True)
    all=ps.items
    pagination = Pagination(
        page=page,
        per_page=limit,
        total=ps.total,
        display_msg="показано <b>{start} - {end}</b> {record_name} из <b>{total}</b>",
        record_name="записей",
        prev_label="<<",
        next_label=">>",
        bs_version=5,
    )
    if id == 0:
        ref = Refs(name="", value="")
    else:
      try:
        res = [r for r in allrefs if r.id == id]
        ref = res[0]
      except:
        ref = Refs(name="", value="")
    
    return render_template(
        "manag.html",
        pagination=pagination,
        title="справочники",
        list=all,
        refs=refs_name,
        r=ref,
    )
  else:
        #если post добавляем запись
        if id != 0:
            ref = db.one_or_404(db.select(Refs).where(Refs.id == id))
            ref.name = request.form["name"]
            ref.value = request.form["value"]
            ref.levelUp = request.form["level"]
            flash(ref.value + " изменено")
        else:
            ref = Refs(name=request.form["name"], value=request.form["value"])
            db.session.add(ref)
            flash(ref.value + " добавлено")
        db.session.commit()

        return redirect("/refs/0")  

@bp.route("/refs/del/<int:id>")
@login_required

def delete(id):
    if session['roles'].count("adminisrators")==0:
      return redirect("/list")  
    ref = db.one_or_404(db.select(Refs).where(Refs.id == id))
    value=ref.value
    db.session.delete(ref)
    db.session.commit()
    flash(value + " удалено")
    return redirect("/refs/0")  

@bp.route("/report")
@login_required

def admin_report():
    report = []
    current_time = datetime.now()
    delta = current_time - timedelta(hours=6)
   
    result = db.session.query(Users).where(Users.created>delta).count()
 
    report.append("новые юзеры за последние 6 часов -"+str(result))
    result = db.session.query(Vacancies).where(Vacancies.result==None).count()
    report.append(" вакансии для проверки -"+str(result))
    result = db.session.query(Preposts).where(Preposts.result==None).count()
    report.append(" анкеты для проверки-"+str(result))
    return jsonify(result=report)

"""     новые юзеры сегодня

    анкеты
    вакансии """
