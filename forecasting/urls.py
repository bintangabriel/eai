from django.urls import path
from .views import *
from .record_views import *
from .predict_views import *

urlpatterns = [
    path('initiateforecasting/', initiate_forecasting),
    path('saveforecasting/', save_forecasting_model),
    path('createforecastingrecord/', create_forecasting_training_record),
    path('updateforecastingrecord/', update_forecasting_training_record),
    path('getforecastingrecord/', get_forecasting_training_record),
    path('lisforecastingtmodel/', list_forecasting_model),
    path('deletemodel/', delete_forecasting_model),
    path('forecast/', forecast),
]