from __future__ import unicode_literals

from django.apps import AppConfig


class CartsConfig(AppConfig):
    name = 'carts'

    def ready(self):
        from . import signals

