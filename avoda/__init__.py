import os
from flask_bootstrap import Bootstrap
from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
login = LoginManager()
login.login_view = "auth.login"


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="fdjlfgjfcafmehtrjq",
        BOOTSTRAP_SERVE_LOCAL=True,
        # SQLALCHEMY_DATABASE_URI = "sqlite:///avoda.db",
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL") or "sqlite:///avoda.db",
        #SQLALCHEMY_ENGINE_OPTIONS={"connect_args": {"connect_timeout": 5}},
        # BOOTSTRAP_BOOTSWATCH_THEME="Cosmo"
        POSTS_PER_PAGE=10,
        SESSION_PERMANENT=False,
        # PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    )

    # initialize the app with the extension
    db.init_app(app)

    migrate = Migrate(app, db)
    bootstrap = Bootstrap(app)
    from avoda import error

    app.register_blueprint(error.bp)
    from avoda import auth

    app.register_blueprint(auth.bp)
    login.init_app(app)

    from avoda import managing

    app.register_blueprint(managing.bp)
    from avoda import posts

    app.register_blueprint(posts.bp)
    return app
