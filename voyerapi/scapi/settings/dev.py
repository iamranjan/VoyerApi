from scapi.settings.base import *  # NOQA (ignore all errors on this line)
CELERY_BROKER_URL = 'amqp://jobs:jobs@localhost:5672/jobs'
KAFKA_PORT = 9093
KAFKA_HOST_MODE = "STATIC"
KAFKA_DEV_HOST = "demo-sc-kafka-01.mgmt.pants.net"

JENKINS = {
    # 'BASE_URL': 'http://localhost:8082',
    'BASE_URL': 'http://192.168.71.2:8082',
    'USERNAME': 'admin',
    'PASSWORD': 'mesos123',
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         # add the db called scapi_dev
#         'NAME': 'scapi_dev',
#         # user called scapi for the permission
#         'USER': 'scapi',
#         'PASSWORD': 'password',
#         'HOST': 'localhost',
#         'PORT': 5432,
#     }
# }

import dj_database_url;
DATABASES['default']=dj_database_url.config();
