# __author__ = 'thund'
# -*- coding: UTF-8 -*-

from flask import redirect, url_for, session
from functools import wraps
from simplekv.memory import DictStore
from flask_kvsession import KVSessionExtension
from flask_mongoengine import MongoEngine

store = DictStore()
kvsession = KVSessionExtension(store)
mongo = MongoEngine()


def login_required(function):
    @wraps(function)
    def wrap(*args, **kwargs):
        # Kiểm tra xem user đang đăng nhập hệ thống hay chưa
        # Nếu chưa thì trả về trang đăng nhập
        # Sử dụng cho tất cả các trang yêu cầu đăng nhập khi truy cập
        # Implement lại hàm kiểm tra thay cho đoạn If bên dưới
        if 'logged_in' in session:
            if not session['logged_in']:
                return redirect(url_for('login'), code=302)
        return function(*args, **kwargs)

    return wrap
