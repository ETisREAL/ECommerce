from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path('demo/', include('ECommerce.demo.urls', namespace='demo')),
]
