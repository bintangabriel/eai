"""eai URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from file import urls as file_urls
from workspace import urls as workspace_urls
from data_cleaning_endpoint import urls as checking_urls
from modeling import urls as modeling_urls
from profiling import urls as profiling_urls
from authentication import urls as authentication_urls
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from forecasting import urls as forecasting_urls
from django.views.static import serve 

from django.conf.urls.static import static
from django.conf import settings

schema_view = get_schema_view(
    openapi.Info(
        title="Lumba API",
        default_version='v1',
    ),
    public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('file/', include(file_urls)),
    path('workspace/', include(workspace_urls),),
    path('preprocess/', include(checking_urls)),
    path('modeling/', include(modeling_urls)),
    path('profiling/', include(profiling_urls)),
    path('authentication/', include(authentication_urls)),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('forecasting/', include(forecasting_urls)),
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
]

#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
