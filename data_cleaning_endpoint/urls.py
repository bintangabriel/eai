from django.urls import path, re_path
from .checking_views import *
from .handling_views import *

urlpatterns = [
    path('null/', null_check),
    path('duplication/', duplication_check),
    path('outlier/', outlier_check),
    path('handle/', cleaning_handler),
    path('boxplot/', get_boxplot),
]