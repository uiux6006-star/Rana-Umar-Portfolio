from django.apps import AppConfig


class BaseConfig(AppConfig):
    name = 'base'
    verbose_name = 'Website'

    def ready(self):
        from . import signals  # noqa: F401  (connects the "Remember me" handler)
