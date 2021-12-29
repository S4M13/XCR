import Settings

import os


class Config(object):
    DEBUG = False
    SECRET_KEY = os.urandom(12)

    SQLALCHEMY_DATABASE_URI = Settings.RECORD_DATABASE_BIND
    SQLALCHEMY_BINDS = {
        'users': Settings.USER_DATABASE_BIND,
        'records': Settings.RECORD_DATABASE_BIND
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
