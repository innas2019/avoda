from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from avoda.db import get_db
import datetime

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
       self.o_kind=["полная"]
       self.sex=""
       self.id=0

       self.created=datetime.datetime.now()
       self.updated = datetime.datetime.now()

   
   def get_len(self):
      conv = str(self.len).replace("{"," ").replace("}"," ")
      return conv.replace("'"," ") 
   
   def get_atr_by_name(self, source):
        dataSource = getattr(self,source)
        return dataSource  

def create_post(form):
   global i
   n_post=Post(form["name"],form["place"],form["phone"],form["text"])
    #для языков из списка
   for f in form.keys():
      if (str(f).find("len")!=-1 and str(f).find("level")==-1) :
         s="len_level"+str(form[f])
         value=str(form[s])
         n_post.len.update({form[f]:value})
   db = get_db()
   try:
      db.execute("INSERT INTO post (name, place, phone, text) VALUES (?,?,?,?)",
                    (n_post["name"],n_post["place"],n_post["phone"],n_post["text"]),
                )
      db.commit()
   except db.Error as e:
    return e
   return "ok"
            

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

@bp.route('/')
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
         np.len=p["len"]
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
      create_post(request.form)
      return redirect(url_for('post.list'))
            
   else:
      
      return render_template('posts/post.html',towns=towns, 
      languages=leng,occupations=o_list, o_kind=o_kind,levels=len_levels )

@bp.route('/post/<int:id>',methods=['GET'])
def post(id):
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