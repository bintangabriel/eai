from django.db import models
from workspace.models import Workspace 

# this model is records for modeling process
# status contains "accepted", "in progress",  "canceled", & "completed"
class ModelTrainingRecord(models.Model):
    status = models.CharField(max_length=100,default="accepted")
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

class MLModel(models.Model):
    name = models.CharField(max_length=100, default='')
    file_name = models.CharField(max_length=100, default='')
    username = models.CharField(max_length=100, default="default")
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    method = models.CharField(max_length=100, default="-")
    algorithm = models.CharField(max_length=100, default="-")
    metrics_scores = models.CharField(max_length=200, default="")
    feature = models.TextField(blank=True)
    target = models.TextField(blank=True)
    n_cluster = models.IntegerField(default=0)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

class ObsegModel(models.Model):
    name = models.CharField(max_length=100, default='')
    file_name = models.CharField(max_length=100, default='')
    username = models.CharField(max_length=100, default="default")
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    method = models.CharField(max_length=100, default="-")
    algorithm = models.CharField(max_length=100, default="-")
    metrics_scores = models.CharField(max_length=200, default="")
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

class ModelKey(models.Model):
    model = models.OneToOneField(MLModel, on_delete=models.CASCADE, primary_key=True)
    key = models.CharField(max_length=100, default='')