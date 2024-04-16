from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
    session,
)
from avoda import db
from avoda.models import Refs
from flask_login import login_required
allrefs={}

# читаем все справочники потом с учетом выбранного языка
def get_refs():
    global allrefs
    ps = db.session.execute(db.select(Refs)).scalars()
    allrefs=ps.all()
    res={}
    for p in allrefs:
        res[str(p.id)]=p.value
    return res

# читаем все справочники
def get_ref(name):
    global allrefs
    res=[]
    if not allrefs:
        ps=db.session.execute(db.select(Refs)).scalars()
        allrefs=ps.all()
    for p in allrefs:
        if p.name==name:
         res.append(p.value)
    return res

bp = Blueprint("mng", __name__)
len = []
towns = []
o_list = []


# функция для показа всех записей справочника
@bp.route("/refs/<int:id>", methods=["POST", "GET"])
@login_required
def refs(id):
    ref = None
    if request.method == "GET":
        res = db.session.execute(db.select(Refs)).scalars()
        all=res.all()
        o_list = [r for r in all if r.name == "occupations"]
        len = [r for r in all if r.name == "levels"]
        towns = [r for r in all if r.name == "places"]
        
        """ len = db.session.execute(db.select(Refs).where(Refs.name == "levels")).scalars()
        towns = db.session.execute(
            db.select(Refs).where(Refs.name == "places")
        ).scalars()
        o_list = db.session.execute(
            db.select(Refs).where(Refs.name == "occupations")
        ).scalars() """
        if id == 0:
            ref = Refs(name="", value="")
        else:
            res = [r for r in all if r.id == id] 
            ref=res[0]        
            print(res,ref.id)   

        return render_template("manag.html", len=len, towns=towns, o_list=o_list, r=ref)
        #return render_template("manag.html", all=all, r=ref)
    else:
        if id != 0:
            ref = db.one_or_404(db.select(Refs).where(Refs.id == id))
            ref.name = request.form["name"]
            ref.value = request.form["value"]
            flash(ref.value + " добавлено")
        else:
            ref = Refs(name=request.form["name"], value=request.form["value"])
            db.session.add(ref)
            flash(ref.value + " изменено")
        db.session.commit()
        
        return redirect("/refs/0")
