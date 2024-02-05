from flask import Blueprint
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
) 
from werkzeug.security import check_password_hash, generate_password_hash
from avoda.db import get_db
import datetime
bp = Blueprint("auth", __name__)

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/')
def title():
   return render_template('title.html',title="добро пожаловать")   

@bp.route('/register', methods=['GET', 'POST'])
def register():
    
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        password2 = request.form['password2']
        error = None
        if password!=password2:
          error="ошибка при вводе пароля"
        if error is None:
            db = get_db()

            try:
                db.execute(
                    "INSERT INTO user (name, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)
    else:
     return render_template('auth/register.html')   

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        username = request.form['name']
        password = request.form['password']
        db = get_db()
    
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE name = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['name']= username
            return redirect(url_for('posts.list'))
     
        flash(error)
    else:
     return render_template('auth/login.html', title="Регистрация")    

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.title'))  
     