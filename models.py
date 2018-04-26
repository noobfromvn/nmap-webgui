# __author__ = 'thund'
# -*- coding: UTF-8 -*-

from datetime import datetime
from mongoengine import *


class Users(Document):
    username = StringField(max_length=25, required=True)
    password = StringField(required=True)
    email = EmailField(required=True)
    created_date = DateTimeField(default=datetime.now())


class Reports(Document):
    user_id = ReferenceField(Users, reverse_delete_rule=CASCADE)
    targets = StringField(required=True)
    task_id = StringField(required=True)
    options = StringField(required=True)
    create_date = DateTimeField(default=datetime.now())
    meta = {
        'indexes': [
            '$targets'
        ],
        'index_background': True,
        'index_drop_dups': True,
        'index_cls': False
    }

