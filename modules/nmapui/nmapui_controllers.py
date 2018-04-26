# __author__ = 'thund'
# -*- coding: UTF-8 -*-

import time
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, session, jsonify
from flask_mongoengine import Pagination
from mongoengine.queryset.visitor import Q
from extensions import login_required
from celery.states import READY_STATES
from libnmap.parser import NmapParser, NmapParserException
from nmap_tasks import celery_pipe, celery_nmap_scan
from models import Reports, Users

nmapui_ctl = Blueprint('nmapui', __name__, template_folder='templates')


@nmapui_ctl.route('/', defaults={'page': 'home.html'})
@nmapui_ctl.route('/views/<path:path>')
def send_views(path):
    return render_template('{0}'.format(path))


@nmapui_ctl.route('/task_statistics')
def task_statistics():
    current_time = datetime.now()
    previous_year = datetime(current_time.year - 1, 1, 1)
    current_year = datetime(current_time.year, 1, 1)

    all_task = Reports.objects.count()
    task_by_current_year = Reports.objects(Q(create_date__gte=current_year) & Q(create_date__lt=current_time)).count()

    previous_month = current_time.replace(day=1, hour=0, minute=0, second=0) - timedelta(days=1)
    previous_month = previous_month.replace(day=1)
    current_month = current_time.replace(day=1, hour=0, minute=0, second=0)

    all_task = all_task
    task_by_current_month = Reports.objects(Q(create_date__gte=current_month) & Q(create_date__lt=current_time)).count()

    previous_day = current_time.replace(hour=0, minute=0, second=0) - timedelta(days=1)
    all_task = all_task
    task_by_today = Reports.objects(
        Q(create_date__gte=current_time.replace(hour=0, minute=0, second=0)) & Q(create_date__ne=current_time)).count()

    _users = Users.objects.count()

    response_content = {
        'year': {
            'all_task': all_task,
            'current_year': task_by_current_year
        },
        'month': {
            'all_task': all_task,
            'current_month': task_by_current_month
        },
        'day': {
            'all_task': all_task,
            'today': task_by_today
        },
        'user': _users
    }

    return jsonify(response_content), 200


@nmapui_ctl.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    scantypes = ['-sT', '-sT', '-sS', '-sA', '-sW', '-sM', '-sN', '-sF', '-sX', '-sU']

    if request.method == 'GET':
        skip = int(request.args['skip'])
        limit = int(request.args['limit'])
        sort_by = request.args['sort_by']
        sort_context = int(request.args['sort_context'])
        search = request.args['search']

        if sort_context == -1:
            sort_by = '-' + sort_by

        query = Reports.objects(user_id=session['current_user']).all().order_by(sort_by)
        if search != '':
            query = Reports.objects(user_id=session['current_user']).filter(targets__contains=search).all().order_by(
                sort_by)

        _nmap_tasks = []
        paginator = Pagination(query, skip / limit + 1, 10)
        _dbreports = paginator.items
        for _dbreport in _dbreports:
            _nmap_task = celery_pipe.AsyncResult(_dbreport['task_id'])
            _report = {
                'id': _nmap_task.id,
                'targets': _dbreport['targets'],
                'options': _dbreport['options'],
                'create_date': _dbreport['create_date'],
                'status': _nmap_task.status,
                'ready': 0
            }
            if _nmap_task.result and 'done' in _nmap_task.result:
                _report.update({'progress': float(_nmap_task.result['done'])})
            elif _nmap_task.result and 'report' in _nmap_task.result:
                _report.update({'progress': 100})
            else:
                _report.update({'progress': 0})
            if _nmap_task.status in READY_STATES:
                _report.update({'ready': 1})
            _nmap_tasks.append(_report)

        response_content = {
            'recordsTotal': Reports.objects.count(),
            'recordsFiltered': paginator.total,
            'data': _nmap_tasks
        }
        return jsonify(response_content), 200

    elif request.method == 'POST':
        data = request.get_json()

        if data['targets'] == '':
            response_content = {
                'code': '403',
                'message': 'The targets is not correct!'
            }
            return jsonify(response_content), 200

        scani = int(data.get('scanTechniques', 0))
        if data.get('ports', '') != '':
            portlist = '-p ' + data.get('ports')
        else:
            portlist = ''
        noping = '-Pn' if data.get('noping', False) else ''
        osdetect = '-O' if data.get('osDetection', False) else ''
        bannerdetect = '-sV' if data.get('bannerDetection', False) else ''
        nse_script = ''
        if data.get('scripts', '') != '':
            nse_script = '--script={0}'.format(data.get('scripts'))
        options = '{0} {1} {2} {3} {4} {5}'.format(scantypes[scani],
                                                   portlist,
                                                   noping,
                                                   osdetect,
                                                   bannerdetect,
                                                   nse_script)
        _celery_task = celery_nmap_scan.delay(targets=str(data['targets']), options=str(options))
        report = Reports(user_id=session['current_user'], task_id=_celery_task.id, targets=data['targets'],
                         options=options)
        report.save()

        response_content = {
            'code': '200',
            'message': 'Successful!'
        }
        return jsonify(response_content), 200


@nmapui_ctl.route('/tasks/<task_id>', methods=['DELETE'])
@login_required
def revoke_tasks(task_id):
    if task_id != '':
        celery_pipe.AsyncResult(task_id).revoke(terminate=True, wait=True, timeout=10, signal='SIGKILL')
        time.sleep(3)
        celery_pipe.AsyncResult(task_id).forget()
        _reports = Reports.objects(task_id=task_id)
        for _report in _reports:
            _report.delete()
    response_content = {
        'code': '200',
        'message': 'The task has been removed!'
    }
    return jsonify(response_content), 200


@nmapui_ctl.route('/report/<report_id>')
@login_required
def nmap_report(report_id):
    _report = None
    if report_id is not None:
        try:
            _resultdict = celery_pipe.AsyncResult(report_id).result
            _resultxml = _resultdict['report']
            _resultxml = _resultxml.encode('ascii', 'ignore')
            _report = NmapParser.parse_fromstring(_resultxml)
        except NmapParserException:
            pass

    _nmap_report = ''
    _nmap_report += 'Starting Nmap {0} ( http://nmap.org ) at {1}\n'.format(_report.version, _report.started)

    for host in _report.hosts:
        if len(host.hostnames):
            tmp_host = host.hostnames.pop()
        else:
            tmp_host = host.address

        _nmap_report += 'Nmap scan report for {0} ({1})\n'.format(tmp_host, host.address)
        _nmap_report += 'Host is {0}.\n'.format(host.status)
        _nmap_report += '  PORT     STATE         SERVICE\n'

        for serv in host.services:
            pserv = '{0:>5s}/{1:3s}  {2:12s}  {3}'.format(
                str(serv.port),
                serv.protocol,
                serv.state,
                serv.service)
            if len(serv.banner):
                pserv += ' ({0})\n'.format(serv.banner)
            else:
                pserv += '\n'
            _nmap_report += pserv
        for script_out in host.scripts_results:
            _nmap_report += "Output of {0}: {1}\n".format(script_out['id'], script_out['output'])
        _nmap_report += 'Fingerprints: ' + '{0}\n'.format(host.os).replace('Fingerprints:', '')
        _nmap_report += 'Uptime: {0}\n'.format(host.uptime)

    response_content = {
        'data': _nmap_report
    }
    return jsonify(response_content)
