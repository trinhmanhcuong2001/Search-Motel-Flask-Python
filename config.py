import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cannot be guess'

    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:123456@localhost:5432/Search-Motel"
    SQLACHEMY_TRACK_MODIFICATIONS = False