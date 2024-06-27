from django.urls import path
from .record_views import *
from .modeling_views import *
from .predict_views import *
from .modeling_api_views import *

urlpatterns = [
    path('initiate/', initiate_modeling),
    path('save/', save_model),
    path('createrecord/', create_training_record),
    path('updaterecord/', update_training_record),
    path('getrecord/', get_training_record),
    path('listmodel/', list_model),
    path('columns/', get_columns_type_by_modeling_method),
    path('predict/', predict_model),
    path('model/<idmodel>/predict/', model_predict_api),
    path('model/<idmodel>/info/', get_model_detail),
    path('deletemodel/', delete_model),
    path('getmodel/', get_model),
    path('getmodelkey/', get_modelkey),
    path('tunneling-checker/', ssh_to_dgx),
    path('download/', download_model)
]