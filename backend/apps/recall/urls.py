from django.urls import path
from . import views

app_name = 'recall'

urlpatterns = [
    path('', views.recall_list, name='recall_list'),
]
