__author__ = 'prathvi'
# -*- coding: utf-8 -*-
from datetime import datetime
import os
import random
import hashlib
import base64
from bson import ObjectId
from mongoengine.queryset import DoesNotExist
from flask_login import LoginManager, login_user
from app import ecom_app
# document statuses (as bits)
ACTIVE = 1
PENDING = 2
DELETED = 4
ARCHIVED = 8
BANNED = 16
import datetime
def hash_password(password):
    salt = base64.urlsafe_b64encode(os.urandom(30))
    salt = unicode(salt)
    hash = hashlib.sha256(password + salt)
    hash = unicode(hash.hexdigest())

    return (salt, hash)

def check_password(raw_password, enc_password, salt):
    # first add the password from the form to the salt
    new_hash = hashlib.sha256(raw_password + salt)
    new_hash = unicode(new_hash.hexdigest())

    # check the new hash with the enc_password. we do this via a constant time
    # compare function to evade timing attacks.
    # see: http://codahale.com/a-lesson-in-timing-attacks/
    if len(enc_password) != len(new_hash):
        return False

    compare = 0
    for a, b in zip(enc_password, new_hash):
        compare |= ord(a) ^ ord(b)

    return compare == 0

from flask.ext.mongoengine import MongoEngine
db = MongoEngine()
from app.mongo_encoder import encode_model


from flask_sauth.models import BaseUser

#from idea.models import Idea
#from team.models import Team

class User(BaseUser):
    username = db.StringField(unique=True)
    fb_id = db.StringField(max_length=50,default="")
    fb_username = db.StringField(max_length=100)
    fb_token = db.StringField(max_length=512)
    fb_public_info = db.DictField()
    first_name = db.StringField(max_length=50,default="")
    last_name = db.StringField(max_length=50,default="")
    salt = db.StringField(max_length=255)
    created = db.DateTimeField(default=datetime.datetime.now)
    datetime_local = db.DateTimeField()
    gender = db.StringField(max_length=20,default="")
    dob = db.StringField(max_length=20,default="")
    unique_id = db.IntField(default=0)
    status = db.IntField(default=ACTIVE) # in cents
    is_auto_created = db.BooleanField(default=True)
    active = db.BooleanField(default=True)
    apns_token =  db.StringField(max_length=512,default="")
    gcm_token =  db.StringField(max_length=512,default="")
    profile_pic =  db.StringField(max_length=512,default="")
    device_type = db.StringField(max_length=40,default="")
    follow_up_count = db.IntField(required=True,default=0)
    notifications = db.ListField()
    reset_token =  db.StringField(max_length=20,default="")
    def is_active(self):
        return self.active

    def get_id(self):
        return str(self.id)

    def is_active(self):
        return self.active

    def is_staff(self):
        return self.staff

    def get_fullname(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_shortname(self):
        return self.first_name

    def serialize(selfi,field):
        return str(field)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

from mongoengine import *
class UserDetail(Document):
    user = db.ReferenceField('User')
    teams = db.ListField(db.ReferenceField('Team'),required=False)
    marked_for_agenda = db.ListField(db.ReferenceField('Idea'),required=False)


from mongoengine.queryset import Q
# this is called by the forms to validate the login credentials
def validate_login_with_username(username, raw_password):
    user_search = User.objects.get((Q(username=username) & Q(status=ACTIVE)))
    if user_search == None:
        user_search = User.objects.get((Q(email=username) & Q(status=ACTIVE)))
        if user_search == None:
            return None

    # we have found a user, lets get the password and salt
    enc_password = user_search['password']
    salt = user_search['salt']

    # check it via the model
    if check_password(raw_password, enc_password, salt):
        # User is all OK, save a copy of the user data into self
        return user_search
    else:
        return None

import facebook
def validate_fb_user(fb_id,access_token):
    user_search = None
    try:
        user_search = User.objects.get(fb_id=fb_id)
    except Exception:
        pass
    if user_search == None:
        return None
    else:
        graph = facebook.GraphAPI(access_token)
        profile = graph.get_object("me")
        if profile['id'] == user_search.fb_id:
            user_search.fb_token = access_token
            user_search.save()
            return user_search
        else:
            return None

# this is called by the forms to validate the login credentials
def validate_login( email, raw_password):
    user_search = None
    try:
        user_search = User.objects.get((Q(email=email) & Q(status=ACTIVE) & Q(is_auto_created=False)))
    except Exception:
        pass
    if user_search == None:
        return None

    # we have found a user, lets get the password and salt
    enc_password = user_search['password']
    salt = user_search['salt']

    # check it via the model
    if check_password(raw_password, enc_password, salt):
        # User is all OK, save a copy of the user data into self
        return user_search
    else:
        return None


from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired,BadSignature
from flask.ext.mongorest.resources import Resource


class Apikey(db.Document):
    user = db.ReferenceField(User)
    full_token = db.StringField(max_length=512, required=True)
    token = db.StringField(max_length=128, required=True)
    created = db.DateTimeField(default=datetime.datetime.now)
    status = db.IntField(default=ACTIVE) # in cents

    # create random key
    def generate_auth_token(self,user, expiration = 3600):
        print ecom_app.config['SECRET_KEY']
        s = Serializer(ecom_app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'id': str(user.unique_id) })


def verify_auth_token(tokenStr):
    s = Serializer(ecom_app.config['SECRET_KEY'])
    try:
        tokenobj = Apikey.objects.get(token = tokenStr)
        print tokenobj.full_token
        data = s.loads(tokenobj.full_token)
    except SignatureExpired:
        return None # valid token, but expired
    except BadSignature:
        return None # invalid token
    except DoesNotExist:
        return None
    print data
    user = User.objects.get(unique_id=str(data['id']))
    return user
