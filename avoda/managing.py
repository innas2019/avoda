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
from avoda.db import get_db


class Ref:
    def __init__(self, _id, _name, _value):
        self.name = _name
        self.id = _id
        self.value = _value


# читаем все справочники
def get_ref(name):
    res = []
    db = get_db()
    q = "select value from refs where name='" + name + "'"
    ps = db.execute(q).fetchall()
    for p in ps:
        res.append(p["value"])
    return res


bp = Blueprint("mng", __name__)
len = []
towns = []
o_list = []


# функция для показа всех записей справочника
@bp.route("/refs/<int:id>", methods=["POST", "GET"])
def refs(id):
    if request.method == "GET":
        len = []
        towns = []
        o_list = []
        db = get_db()
        q = "select * from refs"
        ps = db.execute(q).fetchall()
        new_ref = Ref(0, "", "")
        for p in ps:
            if p["name"] == "levels":
                len.append(Ref(p["id"], p["name"], p["value"]))
            elif p["name"] == "places":
                towns.append(Ref(p["id"], p["name"], p["value"]))
            elif p["name"] == "occupations":
                o_list.append(Ref(p["id"], p["name"], p["value"]))
            if id != 0:
                new_ref = Ref(p["id"], p["name"], p["value"])

        return render_template(
            "manag.html", len=len, towns=towns, o_list=o_list, r=new_ref
        )
    else:
        # new_id = request.form["id"]
        name = request.form["name"]
        value = request.form["value"]
        db = get_db()
        if id == 0:
            db.execute(
                "INSERT INTO refs (name, value) VALUES (?, ?)",
                (name, value),
            )
        else:
            db.execute(
                "update refs set name = ?, value = ? where id=?",
                (name, value, id),
            )
        db.commit()
        return redirect("/refs/0")
