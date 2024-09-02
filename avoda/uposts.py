from flask_paginate import Pagination, get_page_parameter
from flask_login import login_required
from flask import Blueprint, flash, redirect, render_template, request, url_for, session
from avoda import db
from avoda.models import Posts, Preposts
from avoda import managing as m
#from avoda import auth as a
#from avoda import info as i
from datetime import datetime, timezone, timedelta
#import json
#from flask import jsonify
#from sqlalchemy import and_, or_
from avoda.posts import Post
bp = Blueprint("uposts", __name__)

user = ""
towns = []
hierarchy={}
allrefs = {}
results=["отклонить","в объявления","в биржу" ]
def create_post(post, res):
    now = datetime.now(timezone.utc)
    msg="сохранено"
    if post.id==0:
      new_post = Preposts(
        created=now,
        place=post.get_id_from_value(post.place),
        phone=post.phone,
        text=post.text,
        contacts=post.contacts,  
        name=post.name  
      )
      db.session.add(new_post)
    else:
      new_post = db.one_or_404(db.select(Preposts).where(Preposts.id == post.id))
      if res!=None:
          new_post.result=res
          new_post.created=now
      msg="Спасибо за заполнение анкеты. После проверки она появится на нашем сайте "  
    db.session.commit()
    flash(post.phone + " "+msg)
    
    return True

@bp.before_app_request
def load_ref():
    global towns
    global allrefs
    global hierarchy
    # заполняем справочники
    allrefs = m.get_refs()
    towns = m.get_ref("places")
    towns.sort()
    
    hierarchy=m.get_hier_for_search()

@bp.route("/prelist")
@login_required
def list_prepost():
    if session['roles'].count("create_post")==0:
      return redirect("/list")  
    
    query = db.select(Preposts).order_by(Preposts.result)

    # читаем по страницам
    limit = 20
   
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
        bs_version=4,
    )
    
    return render_template(
        "prepost/ulist.html",
        pagination=pagination,
        title="Анкеты соискателей",
        list=all, 
        refs=allrefs,
        results=results        
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
    
@bp.route("/prepost/<int:id>", methods=["GET", "POST"])

def post(id):
    if request.method == "POST":
        form = request.form
        n_post = Post("", form["place"], form["phone"], form["text"])
        n_post.id = id
        n_post.get_from_form(form)
        result=None
        if "res" in form.keys():
           result=form["res"]
        create_post(n_post,result)
        if id==0:
           return redirect("/title")
        else:  
           return redirect("/prelist")
        
    else:
        #method get
        if id==0:
          ps=Post("","","","Ищу работу в сфере ....  Полная занятость ... Языки: русский - родной, иврит - разговорный. Гражданин. Есть права на... ")  
          place=""
        else:
          ps = db.one_or_404(db.select(Preposts).where(Preposts.id == id))
          place = allrefs[ps.place]
                 
        return render_template(
            "prepost/upost.html",
            towns=towns,
            post=ps,
            place=place,
            results=results
        )


@bp.route("/del/<int:id>")
@login_required
def delete(id):
    if session['roles'].count("create_post")==0:
       return redirect("/list")
      
    p = db.one_or_404(db.select(Posts).where(Posts.id == id))
    value = p.phone
    db.session.delete(p)
    db.session.commit()
    flash(value + " удалено")
    return redirect("/prelist")
