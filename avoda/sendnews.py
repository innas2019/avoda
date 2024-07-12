from flask import Flask, Blueprint, render_template,flash,redirect
#from flask_mail import Message
from avoda import db
from flask import current_app, session
from avoda.models import Users, Posts
from avoda.posts import create_query
import logging
import json
import smtplib
from email.mime.text import MIMEText
from flask_login import login_required
bp = Blueprint("mail", __name__)
from datetime import datetime, timezone, timedelta


def send_emailSMTP(subject, sender, recipients, text_body, html_body):

    msg = MIMEText(text_body+" https://avoda.site","plain",'utf-8')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipients
    psw=current_app.config["MAIL_PASSWORD"]
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, psw)
       smtp_server.sendmail(sender, recipients, msg.as_string())
    
def send_news(manualy):
    current_time = datetime.now()
    delta = current_time - timedelta(days=1)
    res = db.session.execute(db.select(Users).where(Users.issend == 1,Users.email!=None)).scalars()
    l = current_app.logger
    l.setLevel(logging.INFO)
    allUsers = res.all()
    m_str = "found users for mail messaging: " + str(len(allUsers))
    if manualy: 
       flash("Найдено пользователей для рассылки "+ str(len(allUsers)))
    l.info(m_str)
    count_mail=0
    for user in allUsers:
        #повторно за сутки не отправляем
        if user. mailsend != None:
              if user.mailsend > delta: 
                  continue
        try: 
            if user.settings != None and user.settings !="":
                filter = json.loads(user.settings)
                query = create_query(filter, 1)
            else:
                query = create_query("", 1)  
            
            news = db.session.execute(query).scalars()
            count = len(news.all())
            if count > 0:
                send_str = "по условиям Вашего поиска найдено " + str(count)+ " новых соискателей"
                send_emailSMTP("from avoda site", current_app.config["MAIL_USERNAME"], user.email, send_str, "email/letter.html")
                l.info(send_str + "send mail for " + user.name)
                count_mail=count_mail+1
                user.mailsend=current_time

        except Exception as ex:
            l.error("SMTP error no " + ex.smtp_code)
            l.error("SMTP error no " + ex.smtp_error)
            l.info("problem with send mail for " + user.name)
            if manualy:         
                flash("проблема с рассылкой для "+user.name)
    
    db.session.commit()
    l.info("send mails "+ str(count_mail))  
    if manualy: 
        flash("Отправлено сообщений "+ str(count_mail))        
    
@bp.route("/mail")
@login_required
def mail_from_app():
    if session['roles'].count("adminisrators")==0:
      return redirect("/list")  
    
    send_news(True)
    return redirect("/users/byname")
