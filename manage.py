# __author__ = 'thund'
# -*- coding: UTF-8 -*-

import getpass
import hashlib
from flask_script import Manager
from app import create_app
from flask_wtf.csrf import generate_csrf
from werkzeug.security import generate_password_hash
from models import Users

app = create_app()
manager = Manager(app)


@app.after_request
def set_csrf_cookie(response):
    response.set_cookie('X-CSRFToken', generate_csrf())
    return response


@manager.command
def runserver():
    """Run in local machine."""
    # app.run(host='0.0.0.0', port=8083, use_reloader=False)
    app.run(host='0.0.0.0', port=8083, debug=app.config['DEBUG'])


@manager.command
def adduser(username, email):
    rval = False
    __p1 = getpass.getpass()
    __p2 = getpass.getpass("Confirm password:")
    if __p1 == __p2 and len(__p1):
        password = generate_password_hash(__p1, method='pbkdf2:sha256', salt_length=10)
        user = Users(username=username, email=email, password=password)
        user.save()
    else:
        print "Error: password do not match"


if __name__ == "__main__":
    manager.run(default_command='runserver')
