from flask import Flask, Blueprint, render_template,flash,redirect
#from flask_mail import Message
from avoda import db
from flask import current_app, session
from avoda.models import Users, Posts
from avoda.posts import create_query
from avoda.info import show_in_title
import logging
import json
import smtplib
from email.mime.text import MIMEText
from flask_login import login_required
bp = Blueprint("mail", __name__)
from datetime import datetime, timezone, timedelta
import random


def send_emailSMTP(subject, sender, recipients, text_body, html_body, send_news):
    head= "<html>  <body> "+text_body+" <p>Для просмотра объявлений перейдите на https://avoda.site"
    end="""<p>-----------------------------------<p>Вы получаете эту рассылку потому, что зарегистрировались на нашем сайте. <p>
    Чтобы отписаться от рассылки перейдите: https://avoda.site/cabinet </p>
    <p>  For unsubscribe click here: https://avoda.site/cabinet </p>    </body></html>"""
    #msg = MIMEText(text_body+" https://avoda.site","plain",'utf-8')
    if send_news==None:
        msg = MIMEText(head+end, "html",'utf-8')
    else:
        md="<p>-----------------------------------<p>Наши новости:<p>"+send_news.head+". "+send_news.text+"<p>"
        msg = MIMEText(head+md+end, "html",'utf-8')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipients
    
    psw=current_app.config["MAIL_PASSWORD"]
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, psw)
       smtp_server.sendmail(sender, recipients, msg.as_string())

#days -  за сколько дней искать объявления   
#добавить в таблицу юзер номер послнднего отправленного поста
def send_news(manualy,days):
    
    current_time = datetime.now()
    delta = current_time - timedelta(hours=20)
    l = current_app.logger
    l.setLevel(logging.INFO)
    all_count = create_query("", days).count()
    count_mail=0
    m_str="new posts:"+str(all_count)
    l.info(m_str) 
    if all_count == 0:
        return
    news=show_in_title()
    user_updated = []
    res = db.session.execute(db.select(Users).where(Users.issend == 1,Users.email!=None)).scalars()
    allUsers = res.all()
    m_str = "found users for mail messaging: " + str(len(allUsers))
    if manualy: 
       flash("Найдено пользователей для рассылки "+ str(len(allUsers)))
    l.info(m_str)
    for user in allUsers:
        #повторно за сутки не отправляем
        if user. mailsend != None:
              if user.mailsend > delta: 
                  continue
        try: 
            if user.settings != None and user.settings !="":
                filter = json.loads(user.settings)
                count = create_query(filter, days).count()
              
            else:
                count = all_count
            
            if count > 0:
                send_str = "По условиям Вашего поиска найдено " + str(count)+ " новых соискателей."
                new_news=None
                if user.lastnews!=news.id:
                    new_news=news
                send_emailSMTP("from avoda site", current_app.config["MAIL_USERNAME"], user.email, send_str, "email/letter.html", new_news)
                l.info(send_str + "send mail for " + user.name)
                count_mail=count_mail+1
                user_updated.append(user.id)
    
        except Exception as ex:
            l.info("problem with send mail for " + user.name)
            if manualy:         
                flash("проблема с рассылкой для "+user.name)
            res = db.session.execute(db.update(Users).where(Users.id.in_(user_updated)).values(mailsend=current_time))
            db.session.commit()
            continue
        
    res = db.session.execute(db.update(Users).where(Users.id.in_(user_updated)).values(mailsend=current_time,lastnews=news.id))
    db.session.commit()
    l.info(user_updated)
    l.info("send mails "+ str(count_mail))  
    if manualy: 
        flash("Отправлено сообщений "+ str(count_mail))        

def mix_post(manualy):
    current_time = datetime.now()
    delta = current_time - timedelta(days=15)
    last = db.session.query(Posts.id).where(Posts.updated > delta).count()
    all  = db.session.query(Posts.id).count()
    l = current_app.logger
    l.info("mix from "+str(all-last)+" to "+str(all))
    for post in range(5):
        id=random.randint(all-last, all)
        try:
            newpost = db.one_or_404(db.select(Posts).where(Posts.id==id))
            newpost.updated=current_time
            db.session.add(newpost)
            l.info("post updated "+str(newpost.id))
            if manualy:
                flash("post updated "+str(newpost.id))
        except:
            l.info("post id not exist "+str(id))
            if manualy:
                flash("post id not exist "+str(id))  
    db.session.commit()    

@bp.route("/mail")
@login_required
def mail_from_app():
    if session['roles'].count("adminisrators")==0:
      return redirect("/list")  
    send_news(True,1)
    return redirect("/users/byname")

@bp.route("/mix")
@login_required
def mix_from_app():
    if session['roles'].count("adminisrators")==0:
      return redirect("/list")  
    
    mix_post(True)
    return redirect("/users/byname")