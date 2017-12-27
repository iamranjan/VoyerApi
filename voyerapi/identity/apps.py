from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = 'identity'
    def ready(self):
        from . import signals
