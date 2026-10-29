"""
URL configuration for epms_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path

from django.urls import include
from rest_framework.routers import DefaultRouter
from api.views.views import (UsersInfoViewSet, ProjectsViewSet, ProjectPhasesViewSet, ReportsViewSet, LogsViewSet,)

from api.views.user_login import user_login
from api.views.load_data import load_data
from api.views.add_data import add_data
from api.views.update_data import update_data
from api.views.delete_data import delete_data

from django.views.generic import TemplateView


router = DefaultRouter()
router.register(r'users', UsersInfoViewSet)
router.register(r'projects', ProjectsViewSet)
router.register(r'phases', ProjectPhasesViewSet)
router.register(r'reports', ReportsViewSet)
router.register(r'logs', LogsViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include(router.urls)),
    path('api/user/login/', user_login, name='user-verify'),
    path('api/data/', load_data, name='load-data'),
    path('api/new/', add_data, name='create-data'),
    path('api/update/', update_data, name='update-data'),
    path('api/delete/', delete_data, name='delete-data'),
    path('', TemplateView.as_view(template_name='企业项目管理系统.html')),
]
