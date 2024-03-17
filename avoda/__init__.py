import os
from flask_bootstrap import Bootstrap
from flask import Flask
from avoda import auth
from avoda import managing
from avoda import posts
from . import db

     #BOOTSTRAP_BOOTSWATCH_THEME="Cosmo"
def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE="avoda.db",
        BOOTSTRAP_SERVE_LOCAL=True,
        
    )
    bootstrap = Bootstrap(app)
    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(managing.bp)
    app.register_blueprint(posts.bp)

    return app
