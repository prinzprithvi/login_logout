import urlparse

from flask import Blueprint, render_template, request, session, redirect, flash, current_app
from flask_login import current_user, login_user, logout_user, login_required
from forms import RegistrationForm, LoginForm, ResetPasswordForm, NewPasswordForm, ChangePasswordForm
from flask_sauth.models import User
#from flask.ext.sendmail import Message
from blinker import signal
from app import ecom_app
import sys,traceback
# import boto
# conn = boto.connect_ses(
#             aws_access_key_id=brilliant_app.config.get("AWS_ACCESS_KEY_ID"),
#             aws_secret_access_key=brilliant_app.config.get("AWS_SECRET_ACCESS_KEY"))

signal_user_registered = signal('user-registered')

auth_views = Blueprint('auth_views', __name__,
                        template_folder='templates')

@auth_views.route('/accounts/login', methods=["GET", "POST"])
def login():
    next_url = request.form.get( "next", None) or request.args.get( "next", None) or session.get("next_url", None)

    if(request.method == "GET" and not next_url and request.referrer):
        urldata = urlparse.urlparse( request.referrer)
        if( urldata.path.find("/accounts") != 0):
            host = request.headers.get("HOST", "")
            if( host and urldata.netloc.find(host) > -1):
                next_url = request.referrer

    if( not next_url): next_url = "/"

    session["next_url"] = next_url

    def do_redirect():
        #del( session["next_url"])
        return redirect( next_url)

    if( current_user.is_authenticated):
        return do_redirect()

    if request.method == "POST":
        login_form = LoginForm( request.form)
        form = login_form
        if(form.validate()):
            login_user( form.user_cache,True)
            is_fresh  = request.form.get( "fresh", None)
            if is_fresh is not None and  is_fresh == "true":
                from flask.ext.login import confirm_login
                confirm_login()

            user = User.objects.get( email=form.email.data)
            if user.active == False:
                flash(u'Your account has been deactivated', 'error')
                kwargs = {"login_form": login_form}
                return render_template( "auth/login.html", **kwargs)
            print "In login : "+form.role.data
            if (form.role.data == "ADMIN"):
                session['role'] = "ADMIN"
                return redirect("/admin/servers")
            if (form.role.data == "USER"):
                session['role'] = "USER"
            return do_redirect()
        else:
            flash_errors(login_form)
            kwargs = {"login_form": login_form}
            return render_template( "auth/login.html", **kwargs)
    else:
        login_form = LoginForm()

    kwargs = locals()
    return render_template("auth/login.html", **kwargs)


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            print error
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))

from app.models import User
from app.utils import random_with_N_digits


@auth_views.route('/accounts/signup', methods=["GET", "POST"])
def signup():
    next_url = request.form.get( "next", None) or request.args.get( "next", None) or session.get("next_url", None)

    if( request.method == "GET" and not next_url and request.referrer):
        urldata = urlparse.urlparse( request.referrer)
        if( urldata.path.find("/accounts") != 0):
            host = request.headers.get("HOST", "")
            if( host and urldata.netloc.find(host) > -1):
                next_url = "/accounts/login"

    next_url = "/accounts/login"

    session["next_url"] = next_url

    def do_redirect():
        #del( session["next_url"])
        return redirect( next_url)

    if( current_user.is_authenticated):
        return do_redirect()

    if request.method == "POST":
        register_form = RegistrationForm( request.form)
        form = register_form

        if(form.validate()):
            user = form.save()
            signal_user_registered.send("flask-satuh", user=user,plan_name = form.plan.data)
            user = User.objects.get(id=user.get_id())
            user.unique_id = random_with_N_digits(6)
            user.roles= list()
            user.roles.append("USER")
            user.p_user_type = form.user_type.data # "ACCOUNT_OWNER"
            #new_user.p_user_type = "ACCOUNT_USER"
            if form.owner_id.data is not None and form.owner_id.data != "":
                owner = None
                try:
                    owner = User.objects.get(id = form.owner_id.data)
                except Exception,e:
                    print e.message
                    type_, value_, traceback_ = sys.exc_info()
                    print traceback.format_exception(type_, value_, traceback_)
                user.owner = owner
                user.billing_enabled = True
            user.active = True
            user.save()
            return do_redirect()
        else:
            flash_errors(register_form)
            kwargs = {"register_form": register_form}
            return render_template( "auth/signup.html", **kwargs)
    else:
        register_form = RegistrationForm()
    kwargs = locals()
    return render_template("auth/signup.html", **kwargs)

@auth_views.route("/accounts/logout")
def logout():
    session.clear()
    logout_user()
    return redirect( "/")

@auth_views.route("/accounts/password/reset", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        form = ResetPasswordForm( request.form)
        if( form.validate()):
            user = User.objects.get( email=form.email.data)
            password_reset_token = user.generate_password_reset_token()
            user.password_reset_token  = password_reset_token
            user.save()
            host = request.headers["HOST"]
            link = "http://%s/accounts/password/reset/%s" % (host, password_reset_token)

            msg = "Hi %s,\n\nSomeone (probably you) requested for a password reset at %s. Please visit the following link if you wish to reset your password:\n\n%s\n\nHave a good day!" % (user.name, host, link)
            # conn.send_email(current_app.config["SERVER_EMAIL"], "[%s] Reset Password" % host, msg, [user.email])
            flash( "Sent you a mail to reset the password. Do remember to check your spam folder as well.", "success")
    else:
        form = ResetPasswordForm()
    return render_template( "auth/reset_password.html", **locals())

@auth_views.route("/accounts/password/reset/<password_reset_token>", methods=["GET", "POST"])
def do_reset_password( password_reset_token):
    user = User.objects( password_reset_token=password_reset_token).first()
    if( not user):
        flash( "Invalid request parameters. Please try resetting again.", "error")
        return redirect( "/accounts/password/reset")

    if request.method == "POST":
        form = NewPasswordForm( request.form)
        if( form.validate()):
            user.set_password( form.password1.data)
            flash( "Your password was changed successfully.", "success")
            return redirect( "/accounts/login")

    form = NewPasswordForm()
    return render_template( "auth/new_password.html", **locals())

@auth_views.route("/accounts/password/change", methods=["GET", "POST"])
@login_required
def change_password():
    c_user = current_user
    if( request.method == "POST"):
        form = ChangePasswordForm( request.form)
        if( form.validate()):
            current_user.set_password( form.password1.data)
            flash( "Your password was changed successfully.", "success")
            return redirect( "/")
    else:
        form = ChangePasswordForm()
    return render_template( "auth/change_password.html", **locals())
