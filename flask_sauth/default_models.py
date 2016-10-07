from flask_sauth.models import BaseUser

class User( BaseUser):
    meta = {"indexes": ["email", "password_reset_token"]}
