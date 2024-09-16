from flask import Flask, Blueprint, render_template,flash,redirect,request
#from flask_mail import Message
from avoda import db
from flask import current_app, session
from avoda.models import News,Advt
import logging
import json
from flask_login import login_required
from flask_paginate import Pagination, get_page_parameter
from datetime import datetime, timezone

bp = Blueprint("info", __name__)

def show_in_title():
  res= db.session.execute(db.select(News).order_by(News.created.desc()).offset(0).limit(1)).scalars()
  allNews = res.all()
  return allNews[0]

def show_adv():
  res= db.session.execute(db.select(Advt).where(Advt.priority!=None).order_by(Advt.created.desc()).offset(0).limit(1)).scalars()
  all = res.all()
  if len(all)>0:
    return all[0]
  return

@bp.route("/showinfo")
def show():
    res = db.session.execute(db.select(News).where(News.priority>0)).scalars()
    pNews = res.all()
    res = db.session.execute(db.select(News).where(News.priority==0).order_by(News.created.desc())).scalars()
    allNews = res.all()
    is_admin=False
    if "roles" in session.keys():
      is_admin= session['roles'].count("adminisrators")!=0

    return  render_template("/news/info.html", pNews=pNews,all=allNews,is_admin=is_admin)

@bp.route("/advert/edit/<int:id>", methods=["GET", "POST"])
@login_required
def advert_create(id):
  if session['roles'].count("adminisrators")==0:
      return redirect("/advert")  
    
  if request.method == "POST":
    form = request.form
    now = datetime.now(timezone.utc)
    adv = Advt(name=form["name"], phone=form["phone"],contacts=form["contacts"],text=form["text"], created=now,priority=form["priority"])  
    if id==0:
       db.session.add(adv)

    else:
      adv = db.one_or_404(db.select(Advt).where(Advt.id == id))  
      adv.name=form["name"]
      adv.phone=form["phone"]
      adv.contacts=form["contacts"]
      adv.text=form["text"]  
      adv.priority=form["priority"]
      adv.created=now

    db.session.commit()
    flash(adv.name + " добавлено")
    return redirect("/advert")
  else:
    if id==0:
      adv = Advt(name="", phone="",contacts="",text="")
    else:
      adv = db.one_or_404(db.select(Advt).where(Advt.id == id)) 
    
    return  render_template("/news/editadvt.html", id=id, adv=adv)

@bp.route("/advert")
@login_required
def list_advert():
    if session['roles'].count("adminisrators")==0:
      query = db.select(Advt).where(Advt.priority!=0).order_by(Advt.created.desc())
    
    else:
      query = db.select(Advt).order_by(Advt.created.desc())

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
        "news/advts.html",
        pagination=pagination,
        title="пользователи",
        list=all        
    )

@bp.route("/info/edit/<int:id>", methods=["GET", "POST"])
@login_required
def info_edit(id):
  
  if session['roles'].count("adminisrators")==0:
      return redirect("/showinfo")  
    
  if request.method == "POST":
    form = request.form
    now = datetime.now(timezone.utc)
    pr=None
    if "priority" in form.keys():
      pr=form["priority"]
    lk=None
    if "link" in form.keys():
      if form["link"]!="":
        lk=form["link"]
    new_n = News(head=form["head"], text=form["text"], link=lk,created=now,priority=pr)  
    if id==0:
       db.session.add(new_n)

    else:
      new_n = db.one_or_404(db.select(News).where(News.id == id))  
      new_n.head=form["head"]
      new_n.text=form["text"]  
      new_n.priority=pr
      new_n.link=lk
      new_n.created=now
    db.session.commit()
    flash(new_n.head + " добавлено")
    return redirect("/showinfo")
  #method GET
  else:
    if id==0:
      new_n = News(head="", text="")
    else:
      new_n = db.one_or_404(db.select(News).where(News.id == id)) 
    
    return  render_template("/news/editnews.html", id=id, n=new_n)
  
#delete news
@bp.route("/infoc/<int:id>")
@login_required
def info_del(id):
  if session['roles'].count("adminisrators")==0:
      return redirect("/showinfo")  
  flash("Пока не работает")
  return redirect("/showinfo")
#renew news
@bp.route("/infoe/<int:id>")
@login_required
def info_renew(id):
  if session['roles'].count("adminisrators")==0:
      return redirect("/showinfo")  
  #last number
  last=db.session.execute(db.select(News).order_by(News.id.desc())).scalar()
  old_n = db.one_or_404(db.select(News).where(News.id == id))   
  old_n.id=last.id+1
  now = datetime.now(timezone.utc)
  old_n.created=now
  db.session.commit()
  flash("Обновлено успешно")
  return redirect("/showinfo")