    # install packages
    $ sudo pip install Flask Flask-Login Flask-PyMongo Flask-Script celery uwsgi

    # install mongodb and rabbitmq
    $ sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927
    $ wget -O- https://www.rabbitmq.com/rabbitmq-release-signing-key.asc |
            sudo apt-key add -
    $ echo "deb http://repo.mongodb.org/apt/ubuntu precise/mongodb-org/3.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.2.list
    $ echo 'deb http://www.rabbitmq.com/debian/ testing main' |
            sudo tee /etc/apt/sources.list.d/rabbitmq.list
    $ sudo apt-get update
    $ sudo apt-get install rabbitmq-server
    $ sudo apt-get install -y mongodb-org

    # start rabbitmq and mongodb
    $ sudo systemctl start mongodb
    $ sudo systemctl enable mongodb
    $ sudo systemctl start rabbitmq-server
    $ sudo systemctl enable rabbitmq-server

    # install nmap
    $ sudo apt-get install nmap
    $ sudo pip install python-libnmap

    # run celery
    $ sudo useradd xxx
    $ sudo cp nmap-webgui /home/xxx
    $ sudo apt-get install supervisord
    $ sudo vi /etc/supervisor/supervisord.conf

```
; supervisor config file

[unix_http_server]
file=/var/run/supervisor.sock   ; (the path to the socket file)
chmod=0700                       ; sockef file mode (default 0700)

[supervisord]
logfile=/var/log/supervisor/supervisord.log ; (main log file;default $CWD/supervisord.log)
logfile_maxbytes=50MB       ; maximum size of logfile before rotation
logfile_backups=10          ; number of backed up logfiles
loglevel=info               ; info, debug, warn, trace
pidfile=/var/run/supervisord.pid ; (supervisord pidfile;default supervisord.pid)
nodaemon=false              ; run supervisord as a daemon
minfds=1024                 ; number of startup file descriptors
minprocs=200                ; number of process descriptors
user=root                   ; default user
childlogdir=/var/log/supervisor            ; ('AUTO' child log dir, default $TEMP)

; the below section must remain in the config file for RPC
; (supervisorctl/web interface) to work, additional interfaces may be
; added by defining them in separate rpcinterface: sections
[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix:///var/run/supervisor.sock ; use a unix:// URL  for a unix socket

; The [include] section can just contain the "files" setting.  This
; setting can list multiple files (separated by whitespace or
; newlines).  It can also contain wildcards.  The filenames are
; interpreted as relative to this file.  Included files *cannot*
; include files themselves.

[include]
files = /etc/supervisor/conf.d/*.conf
```

    $ sudo vi /etc/supervisor/conf.d/celeryd.conf

```
; ==================================
;  celery worker supervisor example
; ==================================

[program:celery]
; Set full path to celery program if using virtualenv
command=celery worker -A tasks --loglevel=INFO

directory=/home/xxx/nmap-webgui/nmap_tasks
user=xxx
numprocs=1
stdout_logfile=/var/log/celery/worker.log
stderr_logfile=/var/log/celery/worker_error.log
autostart=true
autorestart=true
startsecs=10

; Need to wait for currently executing tasks to finish at shutdown.
; Increase this if you have very long running tasks.
stopwaitsecs = 6000

; Causes supervisor to send the termination signal (SIGTERM) to the whole process group.
stopasgroup=true

; Set Celery priority higher than default (999)
; so, if rabbitmq is supervised, it will start first.
priority=1000

```

    $ sudo service supervisor start
    # add a user, start the web app in debug and login
    $ python manage.py adduser <username> <email>
    $ python manage.py runserver

    Default run location is 0.0.0.0:8083
    Originally run on python 2.7, on Ubuntu 16.0.4
