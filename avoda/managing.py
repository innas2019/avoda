from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
) 
from avoda.db import get_db


#читаем все спавочники и добавляем в app
#app.config.from_mapping(
def get_ref(name):
 res=[]
 db = get_db()
 q="select value from refs where name='"+name+"'"
 ps=db.execute(q).fetchall()
 for p in ps:
     res.append(p["value"])
 return res

bp = Blueprint("mng", __name__)     
        
@bp.route('/admin')
def admin():
   return "здесь будет управление справочниками и настройками"