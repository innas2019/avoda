import os
from flask_bootstrap import Bootstrap
from flask import Flask
from avoda import posts
from avoda import auth
from . import db
def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE='avoda.db'
    )
    bootstrap = Bootstrap(app)
   
    db.init_app(app)
    app.register_blueprint(posts.bp)
    app.register_blueprint(auth.bp)
    return app
    
