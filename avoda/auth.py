from flask import Blueprint
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

bp = Blueprint("auth", __name__)


@bp.route('/login',methods = ['POST', 'GET'])
def login():
   global user
   if request.method == 'POST':
         user = request.form['name']
         return redirect(url_for('posts.list'))
   else:
     return render_template('auth/login.html',title="Регистрация")