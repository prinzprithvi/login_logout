from flask import render_template,session,request,Response,abort,Blueprint
from flask_login import current_user, login_required
from app import ecom_app

app_views = Blueprint('app_views', __name__,
    template_folder='templates')


@app_views.route('/', methods=["GET"])
@login_required
def home_page():
    username = current_user.name
    c_user = current_user
    try:
        pass
    except Exception, e:
        print e.message
        # type_, value_, traceback_ = sys.exc_info()
        # print traceback.format_exception(type_, value_, traceback_)

    kwargs = locals()
    return render_template("index.html", **kwargs)