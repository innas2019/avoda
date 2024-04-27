from flask import render_template,Blueprint
from werkzeug.exceptions import HTTPException
bp = Blueprint("errs", __name__)

@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('404.html', title="ничего не найдено"), 404

@bp.app_errorhandler(400)
def internal_error(error):

    return render_template('404.html',title="у нас проблемы"), 400
""" 
@bp.app_errorhandler(Exception)
def not_found_error(error):
    return render_template('404.html',title="у вас проблемы"), Exception """