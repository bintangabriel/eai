from .views import *
from django.urls import path, include
from knox import views as knox_views

urlpatterns = [
    path('register/', RegisterUser, name='register'),
    path('verify_account/', VerifyAccount, name='verify_account'),
    path('login/', Login, name='login'),
    path('logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('get_user/', GetUser, name='get_user'),
    path('update_user_data/', UpdateUser, name='update_user'),
    path('update_user_picture/', UpdateUserPicture, name='update_user_picture'),
    path('update_user_password/', UpdateUserPassword, name='update_user_password'),
    path('deleteuser/', DeleteUser),
    path('list_user/', ListUser),
]