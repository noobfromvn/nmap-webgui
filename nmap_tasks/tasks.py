from celery import Celery, current_task
from libnmap.process import NmapProcess

import celeryconfig
import ipaddress

celery_pipe = Celery('tasks')
celery_pipe.config_from_object(celeryconfig)


@celery_pipe.task(name='tasks.nmap_scan')
def celery_nmap_scan(targets, options):
    def status_callback(nmapscan=None, data=''):
        current_task.update_state(state='PROGRESS',
                                  meta={'done': nmapscan.progress,
                                        'etc': nmapscan.etc})

    if '/' in targets:
        if isinstance(targets, unicode):
            _network = ipaddress.ip_network(targets)
        else:
            _network = ipaddress.ip_network(targets.encode('unicode'))
        targets = [str(ip) for ip in _network.hosts()]
    else:
        targets = targets.encode('ascii', 'ignore')

    nm = NmapProcess(targets, options, event_callback=status_callback)
    rc = nm.sudo_run()

    if rc == 0 and nm.stdout:
        r = nm.stdout
    else:
        r = nm.stderr



    return {'rc': rc, 'report': r}
