from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/data/', views.get_sensor_data, name='sensor_data_api'),
    path('api/irrigate/', views.api_irrigate, name='api_irrigate'),
]
