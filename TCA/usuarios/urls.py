from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as viewsL
from . import views
from django.urls import path, include

urlpatterns = [

    path('validar/', views.login_user),
]