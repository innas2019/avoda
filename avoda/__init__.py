import os
from flask_bootstrap import Bootstrap
from flask import Flask,render_template

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
db = SQLAlchemy()    
def page_not_found(e):
  return render_template('404.html'), 404

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="dev",
        #DATABASE="avoda.db",
        BOOTSTRAP_SERVE_LOCAL=True,
        SQLALCHEMY_DATABASE_URI = "sqlite:///avoda.db",
        #BOOTSTRAP_BOOTSWATCH_THEME="Cosmo"
        POSTS_PER_PAGE = 10
    )
 
# initialize the app with the extension
    db.init_app(app)
    migrate = Migrate(app, db)
    bootstrap = Bootstrap(app)
    from avoda import error
    app.register_blueprint(error.bp)
    from avoda import auth
    app.register_blueprint(auth.bp)
    from avoda import managing
    app.register_blueprint(managing.bp)
    from avoda import posts
    app.register_blueprint(posts.bp)
    
    #app.register_error_handler(404, page_not_found)
    return app


#flask --app avoda db migrate   консольные команды
#flask --app avoda db upgrade