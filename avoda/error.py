from flask import render_template,Blueprint
from werkzeug.exceptions import HTTPException
bp = Blueprint("errs", __name__)
@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('404.html', title="Страница не найдена"), 404

@bp.app_errorhandler(400)
def internal_error(error):

    return render_template('404.html',title="Ошибка в приложении"), 400

@bp.app_errorhandler(500)
def internal_error(error):

    return render_template('404.html',title="Ошибка сервер"), 500
@bp.route("/err")
def custom():
    return render_template('404.html',title="Функция пока не реализована, зарегистрируйтесь еще раз с другим логином"), 500

""" 
@bp.app_errorhandler(Exception)
def not_found_error(error):
    return render_template('404.html',title="у вас проблемы"), Exception """
