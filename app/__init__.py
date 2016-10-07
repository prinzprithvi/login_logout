from flask import Flask,redirect,session
from pymongo import read_preferences
ecom_app = Flask(__name__)

#ecom_app.config["MONGODB_SETTINGS"] = {'DB': "ecom_v1", 'read_preference': read_preferences.ReadPreference.PRIMARY}
ecom_app.config["SECRET_KEY"] = "asgdgs1234SAD~klsajlfs(%*@)#$@($)@#%*$%sfakjlhf"

ecom_app.config.update(
    DEBUG = False,
    TESTING = False,
    MONGODB_SETTINGS = {
        'HOST': '127.0.0.1',#
        'PORT': 27017,
        #'DB': 'pitaya_local',
        'DB': 'ecom_v2',#agrostar_demo
        #'TZ_AWARE': True,
        #'replicaset':"rs0"
    },
)
from flask_mongoengine import MongoEngine
from flask_mongorest import MongoRest
db = MongoEngine(ecom_app)
api = MongoRest(ecom_app)

ecom_app.config["USER_MODEL_CLASS"] = "app.models.User"


from datetime import timedelta
from models import User
from flask_login import LoginManager,current_user


login_manager = LoginManager()
login_manager.needs_refresh_message = (
    u"To protect your account, please reauthenticate to access this page."
    )
login_manager.needs_refresh_message_category = "info"
#login_manager.session_protection = "basic"
login_manager.session_protection = "strong"
ecom_app.config["REMEMBER_COOKIE_DURATION"] = timedelta(minutes=30)

@login_manager.user_loader
def load_user(userid):
    user = User.objects(id=userid).first()

    return user

@login_manager.unauthorized_handler
def unauthorized():
    print "unauthorised"
    session.clear()
    return redirect("/accounts/login")


login_manager.init_app(ecom_app)