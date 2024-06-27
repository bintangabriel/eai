from django.db import models
from workspace.models import Workspace

class File(models.Model):
    file = models.CharField(max_length=100, blank=False, null=False)
    size = models.FloatField(default=0)
    username = models.CharField(max_length=100, default="default")
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    numeric = models.TextField(blank=True)
    non_numeric = models.TextField(blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)