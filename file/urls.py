from django.urls import path, re_path
from .views import FileView
from .listviews import ListFileView
from .folder_views import *

urlpatterns = [
    path('', FileView.as_view()),
    path('list/', ListFileView.as_view()),
    path("object-segmentation/", UploadFolder.as_view())
]