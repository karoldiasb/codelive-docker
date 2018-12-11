
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('',views.home, name='home'),
    path('usuario/novo', views.user_register, name='novo_usuario'),
    path('login', views.user_login, name='logar'),
    path('logout',views.user_logout,name='logout'),
    path('index',views.index, name='index'),
 ]


