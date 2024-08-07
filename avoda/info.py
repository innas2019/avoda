from flask import Flask, Blueprint, render_template,flash,redirect
#from flask_mail import Message
from avoda import db
from flask import current_app, session
from avoda.models import News,Advt
import logging
import json
from flask_login import login_required
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

