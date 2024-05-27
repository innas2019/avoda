#pip install Flask-Mail
from flask import Flask, Blueprint
from flask_mail import Message
from avoda import db, mail
from flask import current_app
from avoda.models import Users,Posts
import logging
import json
from datetime import datetime, timezone, timedelta

bp = Blueprint("mail", __name__)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


@bp.route("/mail")
def test_mail():
    res=db.session.execute(
            db.select(Users).where(Users.issend==1)
        ).scalars()
    l = current_app.logger 
    l.setLevel(logging.INFO)
    allUsers=res.all()
    m_str="found users for mail messaging:"+str(len(allUsers))
    l.info(m_str)
    for user in allUsers:
      if user.settings!=None:
        filter=json.loads(user.settings)
        current_time = datetime.now()
        delta = current_time - timedelta(days=1)
        s=""
        if filter["occupations"] != None:
            s = '%"' + filter["occupations"] + '"%'
        news=db.session.execute(
                db.select(Posts)
                .where(
                    Posts.place == filter["place"]
                    #Posts.occupations.like(s),
                    #Posts.updated > delta,
                )
        ) .scalars() 
       
        count=len(news.all())
        if count>0:
           send_str="найдено новых постов: "+str(count)
           #send_email("from avoda site", current_app.config[MAIL_USERNAME][0], user.email, send_str, "")
           print(send_str+" для "+user.name)
           l.info(send_str+" for "+user.name)
         
    return m_str
   

