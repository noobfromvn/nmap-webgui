# __author__ = 'thund'
# -*- coding: UTF-8 -*-

# -*- coding: utf-8 -*-
#  __author__ = 'thund'

import os
import sys
import json
import logging
import datetime
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, jsonify, request, session, url_for, redirect, send_from_directory
from werkzeug.security import check_password_hash
from werkzeug.exceptions import *
from bson import ObjectId
from models import Users
from extensions import kvsession, mongo, login_required
from modules import nmapui_ctl


class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='[[',
        variable_end_string=']]'
    ))


def create_app():
    """
    Create a flask app
    :return: flask app
    """
    app = CustomFlask(__name__)
    app.secret_key = os.urandom(24)
    app.config.from_pyfile('config.py')

    configure_extensions(app)
    configure_blueprints(app)
    configure_log_handlers(app)
    configure_error_handlers(app)
    configure_main_route(app)

    return app


def configure_extensions(app):
    """
    Init app
    :param app: flask app
    :return: not return
    """
    kvsession.init_app(app)
    mongo.init_app(app)


def configure_blueprints(app):
    """
    Registry flask url
    :param app: flask app
    :return: not return
    """
    app.register_blueprint(nmapui_ctl, url_prefix='/nmapui')


def configure_log_handlers(app):
    """
    Config log
    :param app: flask app
    :return: not return
    """
    log_filename = 'template-frontend.log'
    current_file_path = os.path.abspath(__file__)
    log_dir = os.path.dirname(current_file_path)
    log_dir = os.path.dirname(log_dir)
    log_filename = os.path.join(log_dir, log_filename)

    formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler_rotating_file = RotatingFileHandler(log_filename, maxBytes=10000000, backupCount=5)
    handler_rotating_file.setLevel(logging.INFO)
    handler_rotating_file.setFormatter(formatter)

    handler_console = logging.StreamHandler(sys.stdout)

    app.logger.addHandler(handler_rotating_file)
    app.logger.addHandler(handler_console)

    app.logger.info('App log file: {0}'.format(log_filename))


def configure_error_handlers(app):
    """
    Handle error process
    :param app: flask app
    :return: not return
    """

    @app.errorhandler(400)
    def bad_request(error):
        app.logger.debug(error)
        if type(error.description) == dict:
            return jsonify(error=error.description), 400
        else:
            return jsonify(error={'code': 400,
                                  'message': 'Bad Request.'}), 400

    @app.errorhandler(401)
    def unauthorized_request(error):
        app.logger.debug(error)
        if type(error.description) == dict:
            return jsonify(error=error.description), 401
        else:
            return jsonify(error={'code': 401,
                                  'message': 'Unauthorized Request.'}), 401

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('views/errorOne.html'), 404

    @app.errorhandler(405)
    def request_not_found(error):
        app.logger.debug(error)
        if type(error.description) == dict:
            return jsonify(error=error.description), 405
        else:
            return jsonify(error={'code': 405,
                                  'message': 'The method is not allowed for the requested URL.'}), 405

    @app.errorhandler(415)
    def request_not_support_type(error):
        app.logger.debug(error)
        if type(error.description) == dict:
            return jsonify(error=error.description), 415
        else:
            return jsonify(error={'code': 415,
                                  'message': 'The server does not support the media type transmitted in the request.'}), 415

    @app.errorhandler(UnsupportedMediaType)
    def request_not_support_type_by_exception(error):
        app.logger.debug(error)
        if type(error.description) == dict:
            return jsonify(error=error.description), 415
        else:
            return jsonify(error={'code': 415,
                                  'message': 'The server does not support the media type transmitted in the request.'}), 415

    @app.errorhandler(Exception)
    def default_exception(error):
        app.logger.debug(error)
        if error.message != '':
            return jsonify(error={'code': 500,
                                  'message': error.message}), 500
        else:
            return jsonify(error={'code': 500,
                                  'message': 'Internal Error.'}), 500


def configure_main_route(app):
    """
    Config main url route of app
    :param app: flask app (main app)
    :return:
    """

    @app.route('/')
    def index():
        """
        Render index.html file
        :return: html format
        """
        return render_template('index.html')

    @app.route('/favicon.ico')
    def icon():
        """
        Render favicon.ico file
        :return: html format
        """
        return ''

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """
        Render login.html file
        :return: html format
        """
        if request.method == 'GET':
            return render_template('views/nmapui/login.html')
        else:
            data = request.json
            user = Users.objects.filter(username=data['user']).first()
            if user and check_password_hash(user.password, data['pass']):
                response_content = {
                    'code': 200,
                    'message': 'Done'
                }
                session['logged_in'] = True
                session['current_user'] = user.id
                return jsonify(response_content), 200
            response_content = {
                'code': '403',
                'message': 'Wrong email or password'
            }
            return jsonify(response_content), 403

    @app.route('/logout')
    @login_required
    def logout():
        session.pop('logged_in', None)
        return redirect('/')

    @app.route('/login/status')
    def status():
        # bypass login
        # session['logged_in'] = True
        # session['current_user'] = ObjectId('5a0c0a01cd92af7203631be6')

        if 'logged_in' in session:
            if session['logged_in']:
                return jsonify({'status': True}), 200
        return jsonify({'status': False}), 200

    @app.route('/views/<path:path>')
    def send_views(path):
        return render_template('views/{0}'.format(path))
