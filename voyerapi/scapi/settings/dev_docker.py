from scapi.settings.dev import *  # NOQA (ignore all errors on this line)
CELERY_BROKER_URL = 'amqp://guest:guest@rabbitmq:5672/jobs'
KAFKA_PORT = 9093
KAFKA_HOST_MODE="PROD"
JENKINS = {
    'BASE_URL': 'http://192.168.71.2:8082',
    'USERNAME': 'admin',
    'PASSWORD': 'mesos123',
}
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'scapi_dev',
        'USER': 'scapi',
        'PASSWORD': 'password',
        'HOST': 'postgres',
        'PORT': 5432,
    }
}
JENKINS = {
    'BASE_URL': 'http://192.168.71.2:8082',
    'USERNAME': 'admin',
    'PASSWORD': 'mesos123',
}
