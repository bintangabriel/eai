from django.urls import path, re_path
from .views import WorkspaceView
from .listviews import ListWorkspaceView

urlpatterns = [
    path('', WorkspaceView.as_view()),
    path('list/', ListWorkspaceView.as_view()),
]