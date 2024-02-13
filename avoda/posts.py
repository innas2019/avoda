from warnings import catch_warnings
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)

from avoda.db import get_db
import datetime
import json

bp = Blueprint('posts', __name__)

posts=[]
user=''
class Post:
   def __init__(self,_name,_place,_phone,_text):
       self.name=_name
       self.place=_place
       self.phone =_phone
       self.text=_text
       self.len={}
       self.occupations=[]
       self.o_kind=[]
       self.sex=""
       self.id=0
       self.created=datetime.date.today()
       self.updated = datetime.date.today()
 
   def get_len(self):
      conv = str(self.len).replace("{"," ").replace("}"," ")
      return conv.replace("'"," ") 
   
   def get_atr_by_name(self, source):
        dataSource = getattr(self,source)
        return dataSource

   def get_from_form(self,map):
     for f in map.keys():
      #для языков из списка
      if (str(f).find("len")!=-1 and str(f).find("level")==-1) :
         s="len_level"+str(map[f])
         value=str(map[s])
         self.len.update({map[f]:value})
      elif str(f).find("oc")!=-1:
         self.occupations.append(map[f])
      elif str(f).find("ok")!=-1:
         self.o_kind.append(map[f])   
      elif str(f).find("sex")!=-1:
        self.sex=map[f]

def create_post(n_post):
   db = get_db()
   try:
      db.execute("INSERT INTO post (created, updated, name, place, phone, text, len, occupations, o_kind, sex) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (n_post.created, n_post.updated,n_post.name,n_post.place,n_post.phone,n_post.text,json.dumps(n_post.len),str(n_post.occupations),str(n_post.o_kind),n_post.sex),
                )
      db.commit()
   except db.Error as e:
      flash(e)
      return e
   flash(n_post.name+" добавлено")
   return "ok"
            
def update_post(n_post):
   db = get_db()
   len=""
   try:
      len=json.dumps(n_post.len)
   except json.Error as e:
      print (e)

   try:
      db.execute("update post set updated=?, name=?, place=?, phone=?, text=?, len=?, occupations=?, o_kind=?, sex=? where id=?",
                    (n_post.updated,n_post.name,n_post.place,n_post.phone,n_post.text,len,str(n_post.occupations),str(n_post.o_kind),n_post.sex,n_post.id),
                )
      db.commit()
   except db.Error as e:
      flash(e)
      return e
   flash(n_post.name+" изменено")
   return "ok"

def validation(post):
   if post.place=="":
      return False
   return True


def filters(flt) :
   global posts
   f_posts=[]
   for p in posts:
      isTrue=True
      #для языков из списка
      for f in flt.keys():
         if str(f).find("len")!=-1:
            if p.len.get(flt[f])==None:
               isTrue=False
     
         elif str(f).find("oc")!=-1:
            if p.occupations.count(flt[f])==0:
               isTrue=False 
         #для городов  
         else:
            if flt.get(f)!="-" and p.get_atr_by_name(f)!=flt.get(f):
               isTrue=False
            
      if isTrue:
         f_posts.append(p)
   return f_posts


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/list', methods = ['POST', 'GET'])
def list():
   # список заявок
   db = get_db()
   try:
      posts.clear()
      ps=db.execute("select * from post").fetchall()
      for p in ps:
         np=Post(p["name"],p["place"],p["phone"],p["text"])
         np.id=p["id"]
         print(p["len"])
         np.len=json.loads(p["len"])
         np.occupations=p["occupations"]
         np.o_kind=p["o_kind"]
         np.sex=p["sex"]
         posts.append(np)

   except db.Error as e:
      return e  
   if request.method == 'POST':
      f=filters(request.form)
      return render_template('posts/list.html',title="Выбранные публикации",posts=f,user=user)
   else:  
      return render_template('posts/list.html',title="Все публикации",posts=posts,user=user)
   
@bp.route('/filter')
def filter():
   return render_template('posts/filters.html',towns=towns, languages=leng,occupations=o_list, o_kind=o_kind )

@bp.route('/create',methods = ['POST', 'GET'])
def create():
   if request.method == 'POST':
      form=request.form
      n_post=Post(form["name"],form["place"],form["phone"],form["text"])
      n_post.get_from_form(form)
      if validation(n_post):
         if create_post(n_post):
              flash("Запись добавлена!")
              return redirect(url_for('posts.list'))
        
      return render_template('posts/post.html',towns=towns, post=n_post,
       languages=leng,occupations=o_list, o_kind=o_kind,levels=len_levels )    
   else:
      p=Post('','','','')
      return render_template('posts/post.html',towns=towns, post=p,
      languages=leng,occupations=o_list, o_kind=o_kind,levels=len_levels )

@bp.route('/post/<int:id>',methods=['GET','POST'])
def post(id):
   if request.method == 'POST':
      form=request.form
      n_post=Post(form["name"],form["place"],form["phone"],form["text"])
      n_post.id=id
      n_post.get_from_form(form)
      if validation(n_post):            
         if update_post(n_post):
            return redirect(url_for('posts.list'))
         
      return render_template('posts/post.html',towns=towns, post=n_post,
       languages=leng,occupations=o_list, o_kind=o_kind,levels=len_levels )   
   else:   
      if session["roles"].count("create_post")>0:
         for p in posts:
            if id==p.id:
               return render_template('posts/post.html',towns=towns, post=p,
         languages=leng,occupations=o_list, o_kind=o_kind,levels=len_levels ) 
      else:
         for p in posts:
            if id==p.id:
               return render_template('posts/show_post.html',post=p,list=dir(p), title="Объявление от "+p.name)
         

@bp.route('/search')
def search():
   return render_template('posts/search.html')
   
 
len_levels = ["начинающий","средний", "хороший", "родной"]
leng = ["en","he", "ru"]
towns=["Бат-Ям","Хайфа","Холон","Эйлат"]
o_list=["охрана", "уборка","стройка","завод"]
o_kind=["полная", "частичная" ]