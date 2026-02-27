from django.urls import path
from . import views

app_name = 'expired'

urlpatterns = [
    path('', views.expired_list, name='expired_list'),
]
