__author__ = 'prathvi'
#import mailchimp
from app import ecom_app
@ecom_app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    native = date.replace(tzinfo=None)
    format='%b %d, %Y'
    return native.strftime(format)
from flask import request, abort
from flask_login import  current_user,current_app
from models import Apikey,User,login_user
from functools import wraps
def login_or_key_required(view_function):
    @wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        if 'auth_token' in request.args:
            authorization = request.args['auth_token']
            print authorization
            try:
                api_key = Apikey.objects.get(token__exact=authorization)
                if api_key.user:
                    user = User.objects.get(id=api_key.user.id)
                    login_user(user)
                    setattr(current_user, 'api_key', authorization)
                    return view_function(*args, **kwargs)
                else:
                    abort(401)
            except (TypeError, UnicodeDecodeError,Exception) as e:
                print "Exception here>>>>>>"
                print e.message
                abort(401)

        else:
            return view_function(*args, **kwargs)
    return decorated_function


class ordered_dict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self._order = self.keys()

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        if key in self._order:
            self._order.remove(key)
        self._order.append(key)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self._order.remove(key)

    def order(self):
        return self._order[:]

    def ordered_items(self):
        return [(key,self[key]) for key in self._order]


from random import randint
def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)


from flask import request

def request_wants_json():
    best = request.accept_mimetypes\
    .best_match(['application/json', 'text/html'])
    return best == 'application/json' and\
           request.accept_mimetypes[best] >\
           request.accept_mimetypes['text/html']
