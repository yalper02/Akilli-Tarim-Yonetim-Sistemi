from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # 'url' yerine 'urls' olmalı
    path('admin/', admin.site.urls), 
    path('dashboard/', include('visualization.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
]
