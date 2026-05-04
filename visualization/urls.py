from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/data/', views.get_sensor_data, name='api_data'),
    path('api/irrigate/', views.api_irrigate, name='api_irrigate'),
    path('api/config/', views.api_update_threshold, name='api_update_threshold'),
    path('api/export/', views.api_export_report, name='api_export_report'),
    path('api/profile/', views.api_update_profile, name='api_update_profile'),
]
