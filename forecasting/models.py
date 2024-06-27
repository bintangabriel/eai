from django.db import models
from workspace.models import Workspace 

# this model is records for modeling process
# status contains "accepted", "in progress",  "canceled", & "completed"
class ModelForecastingTrainingRecord(models.Model):
    status = models.CharField(max_length=100,default="accepted")
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

class MLModelForecasting(models.Model):
    name = models.CharField(max_length=100, default='')
    file_name = models.CharField(max_length=100, default='')
    username = models.CharField(max_length=100, default="default")
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    algorithm = models.CharField(max_length=100, default="-")
    metrics_scores = models.CharField(max_length=200, default="")
    period = models.CharField(max_length=100, blank=True)
    target = models.CharField(max_length=100, blank=True)
    steps = models.CharField(max_length=100, blank=True)
    units = models.CharField(max_length=100, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
