# monitor/models.py
from django.db import models

class NetworkData(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    upload_speed = models.FloatField()
    download_speed = models.FloatField()
    signal_strenght= models.FloatField()
    frequency = models.FloatField()
    num_devices = models.IntegerField()
    channel = models.IntegerField()
    antenna_type = models.CharField(max_length=255)
    
    
    predicted_upload_speed = models.FloatField()
    predicted_download_speed = models.FloatField()
    predicted_signal_strenght= models.FloatField()

    def __str__(self):
        return str(self.timestamp)
