BROKER_URL = "amqp://guest:guest@localhost:5672//"
CELERY_IMPORTS = ("tasks", )
CELERY_ENABLE_UTC = True
CELERY_RESULT_BACKEND = "mongodb"
CELERY_MONGODB_BACKEND_SETTINGS = {
    "host": '127.0.0.1',
    "port": 27017,
    "database": 'nmapuidb',
    "taskmeta_collection": "celery_taskmeta",
    }
CELERY_TIMEZONE = 'Asia/Ho_Chi_Minh'
