from flask import Flask, Blueprint, render_template,flash,redirect,request
#from flask_mail import Message
from avoda import db
from flask import current_app, session
from avoda.models import News,Advt
import logging
import json
from flask_login import login_required
from flask_paginate import Pagination, get_page_parameter

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
    res = db.session.execute(db.select(News).where(News.priority!=None)).scalars()
    pNews = res.all()
    res = db.session.execute(db.select(News).where(News.priority==None).order_by(News.created.desc())).scalars()
    allNews = res.all()
    return  render_template("/news/info.html", pNews=pNews,all=allNews)

@bp.route("/advert/create")
def advert_create():
   return  render_template("/news/advt.html")

@bp.route("/advert")
def list_advert():
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