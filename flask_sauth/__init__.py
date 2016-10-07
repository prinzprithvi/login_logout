#!/usr/bin/env python

def init_app( app):
    from flask.ext.sauth.models import init_model
    init_model( app)
