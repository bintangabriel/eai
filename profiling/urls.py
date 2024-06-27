from django.urls import path, re_path
from .views import *

urlpatterns = [
    path('barchart/', get_bar_chart),
    path('describe/', get_data_describe),
    path('columninfo/', get_info_per_column),
]