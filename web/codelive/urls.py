"""codelive URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path, include, re_path
from django.contrib import admin
from django.conf.urls import url, include
from django.contrib.auth import views
from django.contrib.auth import views as auth_views
#from .views import home

from django.conf import settings
from django.urls import path, include, re_path
from django.contrib import admin
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ambiente_codelive.urls')),
    #path('login/$', views.login, name='login'),
    #path('logout/$', views.logout, name='logout'),
    path('auth/', include('social_django.urls', namespace='social')),  # <- Here
] + [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
                       }),

]


admin.site.site_header = 'CodeLive'


