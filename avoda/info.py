from flask import Flask, Blueprint, render_template,flash,redirect
#from flask_mail import Message
from avoda import db
from flask import current_app, session
from avoda.models import News
import logging
import json
from flask_login import login_required
bp = Blueprint("info", __name__)

@bp.route("/showinfo")

def show():
    res = db.session.execute(db.select(News).where(News.priority!=None)).scalars()
    pNews = res.all()
    res = db.session.execute(db.select(News).where(News.priority==None)).scalars()
    allNews = res.all()
    return  render_template("/news/info.html", pNews=pNews,all=allNews)

