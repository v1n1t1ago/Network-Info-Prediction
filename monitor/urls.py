from django.urls import path
from . import views

urlpatterns = [
    path('', views.networking, name='index')
]