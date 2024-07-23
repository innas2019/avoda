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
   
    return  render_template("info.html")

