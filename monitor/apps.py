import sys
from django.apps import AppConfig
from .model import TrainedModel

class MonitorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitor'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def ready(self):
        TrainedModel()