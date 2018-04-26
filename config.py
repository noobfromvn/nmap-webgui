# __author__ = 'thund'
# -*- coding: UTF-8 -*-

DEBUG = True

SESSION_KEY_BITS = 128
SESSION_COOKIE_NAME = 'JSESSIONID'
from datetime import timedelta
PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'xxxxxxxxxx'

# mongodb config
MONGODB_DB = 'nmapuidb'
MONGODB_HOST = '127.0.0.1'
MONGODB_PORT = 27017
MONGODB_USERNAME = ''
MONGODB_PASSWORD = ''
