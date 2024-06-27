from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(MLModel)
admin.site.register(ModelKey)
admin.site.register(ModelTrainingRecord)
admin.site.register(ObsegModel)