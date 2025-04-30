# detection_system/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('toxic_messages/', views.toxic_messages, name='toxic_messages'),
]