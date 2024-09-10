import os
from flask_bootstrap import Bootstrap
from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging.handlers import  RotatingFileHandler
import random
import time  
  
#from flask_mail import Mail

db = SQLAlchemy()
login = LoginManager()
login.login_view = "auth.login"
#mail=None
def create_app():
    #global mail
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="fdjlfgjfcafmehtrjq",
        BOOTSTRAP_SERVE_LOCAL=True,
        #SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL") or "sqlite:///avoda.db",
        # BOOTSTRAP_BOOTSWATCH_THEME="Cosmo"
        POSTS_PER_PAGE=10,
        SESSION_PERMANENT=False,
        # PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
        MAIL_SERVER = 'smtp.gmail.com',
        MAIL_PORT = 465,
        MAIL_USE_SSL = True,
        MAIL_USERNAME = os.environ.get("MAIL_USERNAME"),
        MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    )
    app.config.from_pyfile('config.py')
    # initialize the app with the extension
    db.init_app(app)
    migrate = Migrate(app, db)
    bootstrap = Bootstrap(app)
    
    #mail = Mail(app)
    from avoda import error

    if not os.path.exists("logs"):
        os.mkdir("logs")
    file_handler = RotatingFileHandler(
            "logs/avoda.log", maxBytes=10240, backupCount=10
    )
    file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
    )
  
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info("Avoda start")
    
    app.register_blueprint(error.bp)
    from avoda import auth

    app.register_blueprint(auth.bp)
    login.init_app(app)

    from avoda import managing

    app.register_blueprint(managing.bp)
    from avoda import posts

    app.register_blueprint(posts.bp)

    from avoda import sendnews

    app.register_blueprint(sendnews.bp)
    
    from avoda import info

    app.register_blueprint(info.bp)

    from avoda import uposts

    app.register_blueprint(uposts.bp)

    from avoda import vacancies

    app.register_blueprint(vacancies.bp)
    
    @app.context_processor
    def utility_processor():
        def mycounter():
            curr_time = time.localtime()
            hour=curr_time.tm_hour
            if hour<4:
                return random.randint(1, 5)
            elif hour<6:
                return random.randint(10, 20)
            elif hour<16:
                return random.randint(40, 62)
            else:
                return random.randint(20, 40)
        
        return dict(mycounter=mycounter)
    
    @app.context_processor
    def utility_processor():
        def ver():
            return "2.0"
        return dict(ver=ver)
    
    return app